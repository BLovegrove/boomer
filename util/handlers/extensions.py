import os
from enum import Enum
from loguru import logger

__all__ = []


class Type(Enum):
    COMMAND = "commands"
    EVENT = "events"
    TASK = "tasks"


class Load:
    def search(ext_type: Type) -> list[str]:

        extension_list = []

        for dirpath, dirnames, filenames in os.walk(
            os.path.join("bot", "extensions", ext_type.value)
        ):
            for file in filenames:
                if file.endswith(".py") and not file.startswith("__"):
                    extension = dirpath.split(os.sep)
                    extension.append(file[:-3])
                    ext_string = ".".join(extension)
                    if ext_string not in extension_list:
                        extension_list.append(ext_string)

        logger.success(
            f"{len(extension_list)} {str(ext_type.value).capitalize()[:-1] + "(s)"} loaded"
        )

        return extension_list
