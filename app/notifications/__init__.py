from notifications import *
import importlib

LOADED_MODULES = {}

def get_class(name):
    if (name not in LOADED_MODULES):
        module_path = '%s.%s' % (__name__, name)
        lib = importlib.import_module(module_path)
        LOADED_MODULES[name] = lib

    return LOADED_MODULES[name].API_NOTIFICATION_CLASS


"""

from app.notifications import *
smtp = get_class('smtp')

"""
