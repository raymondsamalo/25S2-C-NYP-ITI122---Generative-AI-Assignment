"""
define singleton design pattern
"""
from aiologic import Lock

def singleton(cls):
    """
    A decorator that transforms a class into a singleton.
    """
    instances = {}
    lock = Lock()
    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]
    return get_instance

