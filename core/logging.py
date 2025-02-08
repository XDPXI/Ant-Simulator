from colorama import Fore, Style


def debug(message: str):
    print(f"{Fore.LIGHTBLACK_EX}DEBUG: {Style.RESET_ALL}{message}")


def info(message: str):
    print(f"{Style.RESET_ALL}INFO: {message}")


def warn(message: str):
    print(f"{Fore.YELLOW}WARNING: {Style.RESET_ALL}{message}")


def error(message: str):
    print(f"{Fore.RED}ERROR: {Style.RESET_ALL}{message}")
