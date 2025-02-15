from datetime import datetime

from colorama import init, Fore, Style

import settings

LOG_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]


def setup(log_level: str):
    init(autoreset=True)
    if log_level not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {log_level}")
    settings.view_log_level = log_level


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def _log_message(level: str, message: str, color: str, level_order: int):
    timestamp = get_current_time()
    log_message = f"{color}{level}: {Style.RESET_ALL}{message}"
    if LOG_LEVELS.index(settings.view_log_level) <= level_order:
        print(f"{timestamp} - {log_message}")


def debug(message: str):
    _log_message("DEBUG", message, Fore.LIGHTBLACK_EX, 0)


def info(message: str):
    _log_message("INFO", message, Style.RESET_ALL, 1)


def warn(message: str):
    _log_message("WARNING", message, Fore.YELLOW, 2)


def error(message: str):
    _log_message("ERROR", message, Fore.RED, 3)
