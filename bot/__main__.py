# core imports
from loguru import logger

# custom imports
from util import cfg, models
from util.handlers.logging import LogHandler


LogHandler.init_logging()


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
