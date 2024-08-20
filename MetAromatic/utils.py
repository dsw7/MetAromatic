from functools import cache
from os import get_terminal_size


@cache
def get_separator() -> str:
    try:
        separator = get_terminal_size()[0] * "-"
    except OSError:
        separator = 25 * "-"

    return separator


def print_separator() -> None:
    print(get_separator())
