"""Settings for the Levenshtein distance service."""
import logging.config

from environs import Env

from common.logging_config import get_logging_config

env = Env()


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

UNIPROT_RESTAPI_ENDPOINT = env.str("UNIPROT_RESTAPI_ENDPOINT", default="https://rest.uniprot.org")
