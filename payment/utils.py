import importlib

__all__ = ['get_class']

def get_class(path):
    module_name, class_name = path.rsplit('.', 1)
    m = importlib.import_module(module_name)
    return getattr(m, class_name)


def code_generator(length=10):
    '23456789abcdefghkrstwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
