import os
from loguru import logger
import requests

from util import cfg

__all__ = []


class Discord:
    def pfp(url: str, commit: bool = True):
        logger.debug("Downloading image...")
        logger.debug(f"URL: {url}")
        url_data = url.split("/")

        image_name = url_data[-1].split("?")[0]
        image_data = requests.get(url).content

        if "guilds" in url_data:
            member_id = url_data[url_data.index("users") + 1]
        elif "embed" in url_data:
            member_id = "default"
        else:
            member_id = url_data[url_data.index("avatars") + 1]

        image_path_relative = os.path.join(
            cfg.path.avatars + "/" + member_id + "/" + image_name
        )
        image_path_absolute = os.path.join(
            cfg.path.root + "/" + cfg.path.avatars + "/" + member_id + "/" + image_name
        )

        if commit:
            logger.debug(f"Creating dir: {os.path.dirname(image_path_absolute)}")
            os.makedirs(os.path.dirname(image_path_absolute), exist_ok=True)
            with open(os.path.abspath(image_path_absolute), "wb") as file:
                logger.debug(f"Saving image...")
                file.write(image_data)

        else:
            logger.debug(
                f"Not creating dir (commit=false): {os.path.dirname(image_path_absolute)}"
            )
            logger.debug(f"Not saving image (commit=false)...")

        return image_path_relative
