from sys import stderr
from colorama import Fore, Style

def print_status(message):
    print(Fore.LIGHTBLUE_EX + message + '\n' + '-' * 50 + Style.RESET_ALL)

def print_message(message):
    print(Fore.GREEN + message + Style.RESET_ALL)

def print_warning(message):
    print(Fore.YELLOW + message + Style.RESET_ALL)

def print_error(message):
    print(Fore.LIGHTRED_EX + message + Style.RESET_ALL, file=stderr)
