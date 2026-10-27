from common import Settings,Logger, Audit
from agents import Agent1

def main() -> None:
    settings = Settings()         # load the setting from the toml file
    logger = Logger(settings)     # Create the log files based on the settings
    audit = Audit(logger)         # use logger to log to audit.log

    agent = Agent1(settings, logger, audit)
    print(agent.run())
    # p_setting(settings):

def p_setting(settings):
    # print(f"settings {settings.setting_data!r}")
    
    print(f"llm data {settings.llm}")
    print(f" model {settings.llm.model}")
    
    # print(f" rag {settings.rag}")
    # print(f" web {settings.web}")
    
if __name__ == "__main__":
    main()