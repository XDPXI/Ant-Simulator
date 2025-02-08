from datetime import datetime

from colorama import Fore, Style


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def debug(message: str):
    timestamp = get_current_time()
    log_message = f"{Fore.LIGHTBLACK_EX}DEBUG: {Style.RESET_ALL}{message}"
    print(f"{timestamp} - {log_message}")

def info(message: str):
    timestamp = get_current_time()
    log_message = f"{Style.RESET_ALL}INFO: {message}"
    print(f"{timestamp} - {log_message}")

def warn(message: str):
    timestamp = get_current_time()
    log_message = f"{Fore.YELLOW}WARNING: {Style.RESET_ALL}{message}"
    print(f"{timestamp} - {log_message}")

def error(message: str):
    timestamp = get_current_time()
    log_message = f"{Fore.RED}ERROR: {Style.RESET_ALL}{message}"
    print(f"{timestamp} - {log_message}")
