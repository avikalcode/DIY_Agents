from common import Settings, Logger, Audit

class Agent1:
    
    NAME = "agent_1"

    def __init__(self, settings: Settings, logger: Logger, audit:Audit):
        self._settings = settings
        self._log = logger.get(self.NAME)
        self._audit = audit

    def run(self) -> str:
        
        self._log.info(
            "%s running (app=%s, env=%s)",
            self.NAME,
            self._settings.app_name,
            self._settings.environment,
        )

        self._audit.record(
            user="user-123",
            agent="support",
            prompt="How do I reset my password?",
            response="Use the password reset link.",
            request_id="req-456",
        )
        return "Hello, World!"