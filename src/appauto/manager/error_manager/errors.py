class NeedRetryOnHttpRC401(Exception):
    """Raised when http response status code is 401"""

    pass


class OperationNotSupported(Exception):
    """Raised when params due to operation not supported."""

    pass
