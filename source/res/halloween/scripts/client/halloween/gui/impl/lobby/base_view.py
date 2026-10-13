# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/base_view.py
from __future__ import absolute_import
import typing
from frameworks.wulf import WindowLayer
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow, LobbyNotificationWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.view_helpers.blur_manager import CachedBlur
from halloween.skeletons.halloween_controller import IHalloweenController
from skeletons.gui.app_loader import IAppLoader

class BaseView(ViewImpl, IGlobalListener):
    DESTROY_ON_EVENT_DISABLED = True
    _hwController = dependency.descriptor(IHalloweenController)

    def onPrbEntitySwitched(self):
        if not self._hwController.isAvailable():
            self._onClose()

    def _subscribe(self):
        super(BaseView, self)._subscribe()
        self._hwController.onEventDisabled += self._onEventDisabled

    def _unsubscribe(self):
        self._hwController.onEventDisabled -= self._onEventDisabled
        super(BaseView, self)._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        super(BaseView, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()

    def _finalize(self):
        self.stopGlobalListening()
        super(BaseView, self)._finalize()

    def _onEventDisabled(self):
        if not self._hwController.isAvailable():
            self._onClose()

    def _onClose(self):
        self.destroyWindow()


class SwitcherPresenter(ViewComponent, IGlobalListener):
    _hwController = dependency.descriptor(IHalloweenController)

    def __init__(self):
        super(SwitcherPresenter, self).__init__(R.aliases.halloween.shared.Switcher())

    def onPrbEntitySwitched(self):
        if not self._hwController.isAvailable():
            self._onClose()

    def _onLoading(self, *args, **kwargs):
        super(SwitcherPresenter, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self._hwController.onEventDisabled += self._onEventDisabled

    def _finalize(self):
        self.stopGlobalListening()
        super(SwitcherPresenter, self)._finalize()
        self._hwController.onEventDisabled -= self._onEventDisabled

    def _onEventDisabled(self):
        if not self._hwController.isAvailable():
            self._onClose()

    def _onClose(self):
        self.destroyWindow()


class HWLobbyWindow(LobbyWindow):
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, wndFlags, decorator=None, content=None, parent=None, layer=WindowLayer.UNDEFINED):
        super(HWLobbyWindow, self).__init__(wndFlags=wndFlags, decorator=decorator, content=content, parent=parent, layer=layer)
        self._blur = None
        return

    def _initialize(self):
        super(HWLobbyWindow, self)._initialize()
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)
        containerManager = self.__appLoader.getApp().containerManager
        if containerManager:
            containerManager.onViewAddedToContainer += self.__onViewLoaded

    def __onViewLoaded(self, _, *args):
        self._blur.enable()

    def _finalize(self):
        if self._blur:
            self._blur.fini()
        containerManager = self.__appLoader.getApp().containerManager
        if containerManager:
            containerManager.onViewAddedToContainer -= self.__onViewLoaded
        super(HWLobbyWindow, self)._finalize()


class HWLobbyNotificationWindow(LobbyNotificationWindow):
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, wndFlags, decorator=None, content=None, parent=None, layer=WindowLayer.UNDEFINED):
        super(HWLobbyNotificationWindow, self).__init__(wndFlags=wndFlags, decorator=decorator, content=content, parent=parent, layer=layer)
        self._blur = None
        return

    def load(self):
        if self._blur is None:
            self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)
        super(HWLobbyNotificationWindow, self).load()
        return

    def _initialize(self):
        super(HWLobbyNotificationWindow, self)._initialize()
        containerManager = self.__appLoader.getApp().containerManager
        if containerManager:
            containerManager.onViewAddedToContainer += self.__onViewLoaded

    def __onViewLoaded(self, _, *args):
        self._blur.enable()

    def _finalize(self):
        if self._blur:
            self._blur.fini()
        containerManager = self.__appLoader.getApp().containerManager
        if containerManager:
            containerManager.onViewAddedToContainer -= self.__onViewLoaded
        super(HWLobbyNotificationWindow, self)._finalize()
