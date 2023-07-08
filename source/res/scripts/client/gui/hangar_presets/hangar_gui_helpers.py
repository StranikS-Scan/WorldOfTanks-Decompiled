# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/hangar_gui_helpers.py
import operator
from functools import wraps
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController

def ifComponentAvailable(componentType=None):

    def decorator(method):

        @wraps(method)
        def wrapper(hangar, *args, **kwargs):
            hangarGuiCtrl = dependency.instance(IHangarGuiController)
            return method(hangar, *args, **kwargs) if hangarGuiCtrl.isComponentAvailable(componentType) else None

        return wrapper

    return decorator


def ifComponentInPreset(componentType=None):

    def decorator(method):

        @wraps(method)
        def wrapper(presetGetter, *args, **kwargs):
            preset = presetGetter.getPreset()
            return method(presetGetter, preset, *args, **kwargs) if preset is not None and componentType in preset.visibleComponents else None

        return wrapper

    return decorator


def hasCurrentPreset(defReturn=None, abortAction=None):

    def decorator(method):

        @wraps(method)
        def wrapper(hangarGuiCtrl, *args, **kwargs):
            currentPreset = hangarGuiCtrl.getCurrentPreset()
            if currentPreset is not None:
                return method(hangarGuiCtrl, currentPreset, *args, **kwargs)
            else:
                return operator.methodcaller(abortAction)(hangarGuiCtrl) if abortAction is not None else defReturn

        return wrapper

    return decorator
