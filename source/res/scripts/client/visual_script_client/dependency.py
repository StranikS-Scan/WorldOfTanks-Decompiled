# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/dependency.py
from importlib import import_module
from types import ModuleType
from typing import List
from constants import IS_EDITOR

def dependencyImporter(*modules):
    if IS_EDITOR:
        return [None] * len(modules)
    else:
        return [ import_module(iModule) for iModule in modules ]
