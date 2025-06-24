import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, Future
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


class CustomFuture(Future):
    def __init__(self, func_name, params):
        super().__init__()
        self.details = {"func": func_name, "params": params}


class CustomThreadPoolExecutor(ThreadPoolExecutor):
    def submit(self, fn, *args, **kwargs):
        # Capture the function name and parameters
        func_name = fn.__qualname__
        params = (args, kwargs)

        # Create a CustomFuture with the function details
        custom_future = CustomFuture(func_name, params)

        # Wrap the function call to allow tracking on CustomFuture
        def wrapper(*args, **kwargs):
            try:
                result = fn(*args, **kwargs)
                custom_future.set_result(result)
            except Exception as e:
                custom_future.set_exception(e)
            return custom_future

        # Submit the wrapped function and return the CustomFuture
        super().submit(wrapper, *args, **kwargs)
        return custom_future

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        if timeout is not None:
            end_time = timeout + time.monotonic()

        # Submit each task as a future and store details in the future
        func_name = fn.__qualname__
        fs = []
        for args in zip(*iterables):
            future = self.submit(fn, *args)
            future.details = {"func": func_name, "params": args}  # Attach details
            fs.append(future)

        # Result iterator with reverse completion order and timeout handling
        def result_iterator():
            try:
                fs.reverse()  # To maintain order as tasks complete
                while fs:
                    future = fs.pop()
                    if timeout is None:
                        yield future.result()
                    else:
                        yield future.result(end_time - time.monotonic())
            finally:
                for future in fs:
                    future.cancel()

        return result_iterator()


def callback(future: CustomFuture):
    try:
        future.result()
        logger.info(f"future succeed. future details: {future.details}")
    except Exception as e:
        logger.error(f"future encounter error: {e}, future details: {future.details}")
        raise e


def check_futures_exception(futures: List[CustomFuture]):
    for fu in futures:
        e = fu.exception()
        if e:
            logger.error(f"future raised exception: {e}, future: {fu}, details: {fu.details}")
            raise e
        logger.debug(f"future succeed. future: {fu}, details: {fu.details}")
