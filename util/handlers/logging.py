import logging
import sys
from loguru import logger

from util import cfg

__all__ = ["LogHandler"]


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class LogHandler:
    def init_logging():
        logging.basicConfig(
            handlers=[InterceptHandler()],
            level="DEBUG" if cfg.log_level == "DEBUG" else "ERROR",
            force=True,
        )
        logger.remove()

        logger_format = "<g>{time:YYYY-MM-DD HH:mm:ss}</> <c>|</> <lvl>{level.name:<8}</> <c>|</> <m>{file:>36}</><y>:{line:<4}</> <c>|</> {message}"
        logger.add(
            sink=sys.stdout,
            level=cfg.log_level,
            colorize=True,
            enqueue=True,
            format=logger_format,
            backtrace=True,
            diagnose=False,
        )
        if cfg.save_log:
            logger.add(
                sink="logs/bot.log",
                level=cfg.log_level,
                rotation="1 day",
                compression="zip",
                colorize=True,
                enqueue=True,
                format=logger_format,
                backtrace=True,
                diagnose=False,
            )

        if cfg.log_level != "DEBUG" and cfg.save_log:
            logger.add(
                sink="logs/debug.log",
                level="DEBUG",
                rotation="1 day",
                compression="zip",
                colorize=True,
                enqueue=True,
                format=logger_format,
                backtrace=True,
                diagnose=False,
            )
