from time import sleep


def retry(func, count: int = 3):
    if count == 0:
        return None
    try:
        return func()
    except:
        sleep(1)
        return retry(func, count - 1)
