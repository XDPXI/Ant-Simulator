from datetime import datetime

from colorama import init, Fore, Style

import settings


def setup(log_level: str):
    init(autoreset=True)
    settings.view_log_level = log_level


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def debug(message: str):
    timestamp = get_current_time()
    log_message = f"{Fore.LIGHTBLACK_EX}DEBUG: {Style.RESET_ALL}{message}"
    if settings.view_log_level == "DEBUG":
        print(f"{timestamp} - {log_message}")


def info(message: str):
    timestamp = get_current_time()
    log_message = f"{Style.RESET_ALL}INFO: {message}"
    if settings.view_log_level == "DEBUG" or settings.view_log_level == "INFO":
        print(f"{timestamp} - {log_message}")


def warn(message: str):
    timestamp = get_current_time()
    log_message = f"{Fore.YELLOW}WARNING: {Style.RESET_ALL}{message}"
    if settings.view_log_level == "DEBUG" or settings.view_log_level == "INFO" or settings.view_log_level == "WARN":
        print(f"{timestamp} - {log_message}")


def error(message: str):
    timestamp = get_current_time()
    log_message = f"{Fore.RED}ERROR: {Style.RESET_ALL}{message}"
    if settings.view_log_level == "DEBUG" or settings.view_log_level == "INFO" or settings.view_log_level == "WARN" or settings.view_log_level == "ERROR":
        print(f"{timestamp} - {log_message}")
