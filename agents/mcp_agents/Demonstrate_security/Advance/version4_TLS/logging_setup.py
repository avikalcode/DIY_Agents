import logging
import logging.handlers
import re
import uuid
from pathlib import Path

LOG_DIR = Path(__file__).parent/ "logs"
LOG_DIR.mkdir(exist_ok=True)

# Never write credentials into a log file. 
# If a developer accidentally writes code like logging.info(f"User authenticated with token: {user_token}"),
# this code intercepts that message in the background. Instead of saving the real token, 
# it ensures the log file only contains: User authenticated with token: [REDACTED-JWT].
import re

# # 1. Create the search rule object
# token_pattern = re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]+")

# # 2. A sample log message containing a dangerous secret
# log_message = "DEBUG: Request sent with Header: Bearer secretToken123_abc.xyz+/="

# # 3. Use the object to redact the secret
# safe_message = token_pattern.sub("Bearer [REDACTED]", log_message)

# print(safe_message)
# # Output: DEBUG: Request sent with Header: Bearer [REDACTED]

# 1. Create the search rule object
_SECRETS = [
#   (       search pattern                      ,  replacement test  )
    (re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]+"), "Bearer [REDACTED]"), # a regular expression search pattern
    (re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+")   , "[REDACTED-JWT]"),
]

# This class is responsible for setting the log format and replace text that matched pattern that have Bearer token or looks lke JWT token
class RedactingFormatter(logging.Formatter):
    
    def format(self, record):
        text = super().format(record)        # includes the traceback
        
        for pattern, repl in _SECRETS:
            text = pattern.sub(repl, text) # It scans the entire log string. finds a matching token, it swaps it out for the safe [REDACTED] text.
        
        return text

def _build():
    # File logger: full detail, rotated, never shown on the console
    file_log = logging.getLogger("app.file")
    file_log.setLevel(logging.DEBUG)
    file_log.propagate = False
    if not file_log.handlers:
        fh = logging.handlers.RotatingFileHandler(
            LOG_DIR / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setFormatter(RedactingFormatter("%(asctime)s %(levelname)s %(message)s"))
        file_log.addHandler(fh)

    # Console logger: generic messages only
    console_log = logging.getLogger("app.console")
    console_log.setLevel(logging.INFO)
    console_log.propagate = False
    if not console_log.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        console_log.addHandler(ch)
    return file_log, console_log

file_log, console_log = _build() # File and Console log object


# a generator that completely flattens nested ExceptionGroup objects down to their individual, core exceptions.
"""Flatten ExceptionGroups so we log the real errors inside them."""
def _leaves(exc: BaseException):   

    subs = getattr(exc, "exceptions", None) # This line safely checks if the exception has sub-errors. If it does, they are assigned to subs; if not, subs becomes None
    
    if subs:
        for s in subs: # If sub-exceptions exist, the function loops through each one (s) and calls itself recursively (_leaves(s)).
            yield from _leaves(s) # The "yield from"  statement acts like a pipe, passing the final, flattened errors all the way back up to the original caller.
    else:
        yield exc # If the exception is a standard, single error (or if the function has successfully drilled down to the absolute bottom of a group), it hits this block. It "yields" (returns one by one) that single, real exception to the caller.


# Log in the file
def log_detail(exc: BaseException, context: str = "") -> str:
    """Write full detail to the file only. Returns a short reference id."""
    ref = uuid.uuid4().hex[:8]
    for leaf in _leaves(exc):
        file_log.error("[%s] %s | %s: %s", ref, context, type(leaf).__name__, leaf,
                       exc_info=(type(leaf), leaf, leaf.__traceback__))
    return ref

    
# log in the console 
# call the function to log in the file
def report(user_msg: str, exc: BaseException, context: str = "") -> str:
    """Detail to the file, generic message plus ref to the console."""
    ref = log_detail(exc, context)
    console_log.error("%s (ref: %s)", user_msg, ref)
    return ref

# it only wraps the call that starts async code
# It runs main() and catches any uncaught exception, including ones wrapped in an ExceptionGroup. 
# It then writes the full detail to logs/app.log and prints a generic line with a reference id to the console. 
# That’s the “detail in the file, generic message on the console” behavior
import anyio
def run_main(coro_fn, user_msg="The operation failed. See the log for details.", context=""):
    try:
        anyio.run(coro_fn)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        report(user_msg, e, context=context)