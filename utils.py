import time
from contextlib import contextmanager

@contextmanager
def timer(name, log=None):
    """ Convenience wrapper to measure execution time of a code block.
        Prints out the runtime to a given log handle or stdout.

        Usage:
        from src.util import timer
        with timer('my_code', my_log):
            # your code here

        This will output something like "my_code took 1.308s" to my_log.debug()
    """

    start = time.time()
    try:
        yield None
    finally:
        end = time.time() - start
        text = '%s took %.03fs'
        if log:
            log.debug(text, name, end)
        else:
            print(text % (name, end))
