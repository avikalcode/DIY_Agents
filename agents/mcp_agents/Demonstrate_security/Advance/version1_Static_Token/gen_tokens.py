import secrets
print("TODO_TOKEN_ALICE=" + secrets.token_urlsafe(32))
print("TODO_TOKEN_BOB=" + secrets.token_urlsafe(32))

# This generates a cryptographically strong, random 32-byte string (about 43 characters long) using letters, numbers, -, and _. Because it is completely random rather than a structured token like a JWT, the server must store a copy of it to recognize it later


# set this value in your environment before running the server, e.g.:
# export TODO_TOKEN_ALICE=...
# export TODO_TOKEN_BOB=...

# powershell:
# $env:TODO_TOKEN_ALICE = "..."
# $env:TODO_TOKEN_BOB = "..."