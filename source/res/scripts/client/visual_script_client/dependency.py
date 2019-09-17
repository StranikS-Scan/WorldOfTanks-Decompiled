# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/dependency.py
from functools import wraps
from importlib import import_module
from types import ModuleType, FunctionType
from typing import List
from constants import IS_EDITOR

def editorValue(value):

    def wrapper(func):

        @wraps(func)
        def wrapperFunc(*args, **kwargs):
            return value if IS_EDITOR else func(*args, **kwargs)

        return wrapperFunc

    return wrapper


def dependencyImporter(*modules):
    if IS_EDITOR:
        return [None] * len(modules)
    else:
        return [ import_module(iModule) for iModule in modules ]
