import logging
import logging.handlers
import colorlog


def get_logger(
    name: str,
    debug_primary: str = "cyan",
    debug_secondary: str = "bold_white",
    info_primary: str = "bold_purple",
    info_secondary: str = "white",
    warning_primary: str = "bold_black,bg_yellow",
    warning_secondary: str = "bold_yellow",
    error_primary: str = "bold_whote,bg_red",
    error_secondary: str = "bold_red",
    critical_primary: str = "bold_white,bg_red",
    critical_secondary: str = "bold_red"
) -> logging.Logger:

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message_log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": debug_primary,
            "INFO": info_primary,
            "WARNING": warning_primary,
            "ERROR": error_primary,
            "CRITICAL": critical_primary,
        },
        secondary_log_colors={
            "message": {
                "DEBUG": debug_secondary,
                "INFO": info_secondary,
                "WARNING": warning_secondary,
                "ERROR": error_secondary,
                "CRITICAL": critical_secondary
            }
        },
        style="%"
    )

    console_logger = logging.StreamHandler()
    console_logger.setFormatter(formatter)

    logger = colorlog.getLogger(name)
    logger.addHandler(console_logger)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    return logger
