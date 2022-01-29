# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_base_main_view_component.py
import weakref
import typing
from frameworks.wulf import ViewModel
from sound_gui_manager import ViewSoundExtension
TViewModel = typing.TypeVar('TViewModel', bound=ViewModel)

class BaseLunarNYViewComponent(typing.Generic[TViewModel], object):
    __slots__ = ('_viewModel', '_isLoaded', '_isActive', '_mainViewRef', '__soundExtension')
    _SOUND_SPACE_SETTINGS = None

    def __init__(self, viewModel, view):
        super(BaseLunarNYViewComponent, self).__init__(viewModel)
        self._isActive = False
        self._mainViewRef = weakref.proxy(view)
        self.__soundExtension = LunarComponentSoundExtension(self._SOUND_SPACE_SETTINGS)
        self._viewModel = viewModel
        self._isLoaded = False

    def onLoading(self, initCtx, isActive):
        self.setActive(isActive)

    def onLoaded(self):
        self._isLoaded = True
        if self._isActive:
            self.__soundExtension.enable()

    def isLoaded(self):
        return self._isLoaded

    def getIsActive(self):
        return self._isActive

    def setActive(self, isActive):
        if self._isActive != isActive and isActive and self._isLoaded:
            self.__soundExtension.enable()
        elif self._isActive != isActive and not isActive and self._isLoaded:
            self.__soundExtension.disable()
        self._isActive = isActive

    def createToolTipContent(self, event, contentID):
        return None

    def initialize(self, *args, **kwargs):
        self._addListeners()

    def finalize(self):
        self._removeListeners()
        self._viewModel = None
        self.__soundExtension.disable()
        return

    def _addListeners(self):
        pass

    def _removeListeners(self):
        pass


class LunarComponentSoundExtension(object):
    __slots__ = ('__soundExtension', '__isEnabled')

    def __init__(self, settings):
        self.__soundExtension = ViewSoundExtension(settings)
        self.__isEnabled = False

    def enable(self):
        if not self.__isEnabled:
            self.__soundExtension.initSoundManager()
            self.__soundExtension.startSoundSpace()
            self.__isEnabled = True

    def disable(self):
        if self.__isEnabled:
            self.__soundExtension.destroySoundManager()
            self.__isEnabled = False
