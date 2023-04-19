"""Settings for the Levenshtein distance service."""
import logging.config
from environs import Env

logger = logging.getLogger(__name__)

env = Env()

def get_logging_config(env, loggers_to_silent=None):
    """Return the python logging configuration based on environment variables.
    The log level for the given loggers_to_silent will be set to INFO.
    Use this for loggers that at DEBUG level put too much entries that we never take care.
    
    The log level for specific loggers can be more customized with the CUSTOM_LOGGING environment
    variable, providing a list of logger and level in the form: CUSTOM_LOGGING=<logger>=<LEVEL>
    This will overwrite the configuration set because of loggers_to_silent (so can be used to put
    to DEBUG some of the silenced loggers).
    Example:
        CUSTOM_LOGGING=botocore=DEBUG,elasticsearch=WARNING
    """
    log_handlers = env.list("LOG_HANDLERS", default=["console"])

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {},
        "handlers": {},
        "loggers": {
            "": {
                "handlers": log_handlers,
                "level": env.str("LOG_LEVEL", default=env.str("GENERAL_LOGGING_LEVEL", default="DEBUG")),
            },
        },
    }

    if "console" in log_handlers:
        _update_logging_config(logging_config, _get_console_config(env))

    if loggers_to_silent:
        for logger in loggers_to_silent:
            logging_config["loggers"][logger] = {
                "level": "INFO",
            }

    for logger_config in env.list("CUSTOM_LOGGING", default=[]):
        logger, level = logger_config.split("=")
        logging_config["loggers"][logger] = {
            "level": level,
        }

    return logging_config


def _update_logging_config(logging_config: Dict, config: Dict):
    logging_config["formatters"].update(config.get("formatters", {}))
    logging_config["handlers"].update(config.get("handlers", {}))


def _get_console_config(env: Env) -> Dict:
    return {
        "formatters": {
            "simple": {
                "format": "%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": env.str("LOG_LEVEL", default=env.str("CONSOLE_LOGGING_HANDLER_MIN_LEVEL", default="WARNING")),
                "formatter": "simple",
            },
        },
    }


# The logging must to be the first thing to configure to get the logs raised here
LOGGING = get_logging_config(
    env,
    loggers_to_silent=[
        # The following loggers put lot of DEBUG entries and we only care if there is some error
        # to show the DEBUG level, use the CUSTOM_LOGGING env variable
        "urllib3.util.retry",
        "urllib3.connectionpool",
    ],
)
logging.config.dictConfig(LOGGING)
