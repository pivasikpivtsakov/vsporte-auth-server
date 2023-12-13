import logging
import os
from typing import Callable

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


def _env_get(
        varname: str,
        validation_rule: Callable[[str], bool] | None = None,
        warning_message: str | None = None,
        raise_if_failed=True
) -> str | None:
    """
    :param varname: name of env var
    :param validation_rule: returns True if var passes validation
    :param warning_message: what to print in logs if validation fails
    :param raise_if_failed: raise if var is None or validation failed
    :return: env var value
    """
    varvalue = os.getenv(varname)
    if not varvalue:
        logger.warning(f"{varname} is unset!")
        if raise_if_failed:
            raise Exception(f"{varname} is unset!")
    if validation_rule is not None:
        if not validation_rule(varvalue):
            logger.warning(warning_message)
            if raise_if_failed:
                raise Exception(f"validation failed for {varname}")
    return varvalue


DB_USER = _env_get("DB_USER")
DB_PASS = _env_get("DB_PASS")
DB_HOST = _env_get("DB_HOST")
DB_PORT = _env_get("DB_PORT")
DB_NAME = _env_get("DB_NAME")
SECRET_KEY = _env_get("SECRET_KEY", raise_if_failed=False)
