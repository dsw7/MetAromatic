from sys import stderr
from colorama import Fore, Style

def print_message(message):
    print(Fore.GREEN + 'UPDATE: ' + message + Style.RESET_ALL)

def print_warning(message):
    print(Fore.YELLOW + 'WARNING: ' + message + Style.RESET_ALL)

def print_error(message):
    print(Fore.LIGHTRED_EX + 'ERROR: ' + message + Style.RESET_ALL, file=stderr)
