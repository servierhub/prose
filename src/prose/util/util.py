import json
import sys
import hashlib

from time import sleep
from typing import Callable, TypeVar

from termcolor import colored

T = TypeVar('T')
def retry(func: Callable[..., T], *args, count: int = 3) -> T | None:
    """
    Retries calling a given function with arguments a specified number of times.

    Args:
        func (Callable[..., T]): The function to be called and retried.
        *args: Variable-length argument list to pass to the function.
        count (int): The number of times to retry the function call. Default is 3.

    Returns:
        None (if all retries fail) or the return value of the function call.
    """
    if count == 0:
        return None

    try:
        return func(*args)
    except:
        sleep(1)
        return retry(func, *args, count=count - 1)


def panic(msg: str) -> None:
    """
    Prints an error message in red color and exits the program with a status code of 1.

    Args:
        msg (str): The error message to be displayed.

    Returns:
        None
    """
    print(
        colored(
            "\r" + msg,
            "red",
            attrs=["bold"],
        ),
        file=sys.stderr
    )
    sys.exit(1)


def get_digest_string(s: str) -> str:
    return hashlib.sha256(s.encode('UTF-8')).hexdigest()


def get_digest_object(s: dict | list[dict] | list[str]) -> str:
    return hashlib.sha256(json.dumps(s).encode('UTF-8')).hexdigest()


def get_digest_file(filename: str) -> str:
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest() # type: ignore
