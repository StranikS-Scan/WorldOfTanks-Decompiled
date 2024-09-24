# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/view_overrider.py
import typing
import Event
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from typing import Callable, Any, Dict, Tuple, Optional, Union
    from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, ViewLoadParams

class ViewOverrider(object):
    __slots__ = ('__delegates', 'onViewOverriden', '__lastOverrides')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        self.__delegates = {}
        self.__lastOverrides = {}
        self.onViewOverriden = Event.Event()

    def getOverrideData(self, loadParams, *args, **kwargs):
        alias = loadParams.viewKey.alias
        for delegate in self.__delegates.get(alias, ()):
            overrideData = delegate(loadParams, *args, **kwargs)
            if overrideData and overrideData.checkCondition(*args, **kwargs):
                overrideData.prepareAdditionalParams(loadParams, *args, **kwargs)
                self.__lastOverrides[alias] = overrideData.loadParams.viewKey.alias
                self.onViewOverriden(alias, overrideData)
                return overrideData

        self.__lastOverrides.pop(alias, None)
        return

    def addOverride(self, alias, delegate):
        self.__delegates.setdefault(alias, set()).add(delegate)

    def removeOverride(self, alias, delegate):
        self.__delegates.get(alias, set()).discard(delegate)

    def isViewOverriden(self, alias):
        contentResId = self.__lastOverrides.get(alias)
        return contentResId is not None and self.__gui.windowsManager.getViewByLayoutID(contentResId) is not None


class OverrideData(object):
    __slots__ = ('__loadParams', '__args', '__kwargs')

    def __init__(self, loadParams, *args, **kwargs):
        self.__loadParams = loadParams
        self.__args = args
        self.__kwargs = kwargs

    @property
    def loadParams(self):
        return self.__loadParams

    @property
    def args(self):
        return self.__args

    @property
    def kwargs(self):
        return self.__kwargs

    def checkCondition(self, *args, **kwargs):
        raise NotImplementedError

    def prepareAdditionalParams(self, params, *args, **kwargs):
        pass

    def getFadeCtx(self):
        return None
