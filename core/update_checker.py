import settings
from core import logging


def check_updates():
    try:
        with open("version.txt", "r") as version_file:
            current_version = version_file.read().strip()
            logging.info(f"Your current version is {current_version}.")
            if current_version != settings.version:
                logging.warn("A new version is available. Consider updating Ant Simulator.")
            else:
                logging.info("Ant Simulator is up-to-date.")
    except FileNotFoundError:
        logging.error("Error: version.txt file not found.")
