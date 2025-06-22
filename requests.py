class RequestException(Exception):
    pass

class exceptions:
    RequestException = RequestException

def get(*args, **kwargs):
    raise RequestException('Network disabled')
