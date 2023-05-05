
'''
    utils
'''
import sys

def inject_module(module_name, module):
    sys.modules[module_name] = module

def append_module(parent_module, name, module):
    setattr(parent_module, name, module)
    # https://stackoverflow.com/questions/19883870/python-from-x-import-not-importing-everything
    parent_module.__all__.append(name)

def lowerstrify(obj):
    if type(obj) is bytes:
        obj = obj.decode('ascii')
    return obj.lower()
