# core imports
from loguru import logger

# custom imports
import util.config as cfg
from util import models
from util.handlers import logging


logging.init_logging()


def main():
    bot = models.LavaBot()

    bot.run(cfg.bot.token, log_handler=None)
    logger.info(
        "# ---------------------------------------------------------------------------- #"
    )
    logger.info(
        "#                             BOT SHUTDOWN COMPLETE                            #"
    )
    logger.info(
        "# ---------------------------------------------------------------------------- #"
    )


if __name__ == "__main__":
    main()
