import logging
import logging.handlers
import colorlog


def get_logger(name: str) -> logging.Logger:

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message_log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "bold_purple",
            "WARNING": "bold_black,bg_yellow",
            "ERROR": "bold_white,bg_red",
            "CRITICAL": "bold_white,bg_red",
        },
        secondary_log_colors={
            "message": {
                "DEBUG": "bold_white",
                "INFO": "white",
                "WARNING": "bold_yellow",
                "ERROR": "bold_red",
                "CRITICAL": "bold_red"
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
