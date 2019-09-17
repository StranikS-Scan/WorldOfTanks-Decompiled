# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/registrar.py
import inspect
from constants import IS_CLIENT, IS_CELLAPP, IS_EDITOR
from component import Component, ASPECT
__all__ = ['regVScriptComponent',
 'regAllVScriptComponentsInModule',
 'getComponents',
 'aspectActive',
 'anyAspectActive']
__PY_VISUAL_SCRIPT_COMPONENTS = []
__VS_ENGINE_LOAD_COMPONENTS = False

def __findVScriptConponentsInModule(module):
    return list((value for key, value in inspect.getmembers(module, inspect.isclass) if issubclass(value, Component) and value is not Component))


def aspectActive(aspect):
    if IS_EDITOR:
        return True
    if aspect is ASPECT.CLIENT:
        return IS_CLIENT
    return IS_CELLAPP if aspect is ASPECT.SERVER else False


def anyAspectActive(*aspects):
    return any(map(aspectActive, aspects))


def regVScriptComponent(value):
    if value not in __PY_VISUAL_SCRIPT_COMPONENTS:
        __PY_VISUAL_SCRIPT_COMPONENTS.append(value)


def regAllVScriptComponentsInModule(module):
    for component in __findVScriptConponentsInModule(module):
        regVScriptComponent(component)


def getComponents():
    global __VS_ENGINE_LOAD_COMPONENTS
    __VS_ENGINE_LOAD_COMPONENTS = True
    return __PY_VISUAL_SCRIPT_COMPONENTS
