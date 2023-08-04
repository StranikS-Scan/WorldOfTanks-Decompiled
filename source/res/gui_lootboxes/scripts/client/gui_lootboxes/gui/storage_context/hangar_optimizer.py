# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/storage_context/hangar_optimizer.py
import enum
import AnimationSequence
import BigWorld
import WebBrowser
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.shared.event_dispatcher import showHangar
from helpers import dependency, isPlayerAccount
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared.utils import IHangarSpace

class _HangarOptimizerStates(enum.IntEnum):
    ENABLED = 1
    DISABLED = 2
    DISABLING = 3


class HangarOptimizer(object):
    __slots__ = ('__state',)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __gui = dependency.descriptor(IGuiLoader)
    __appFactory = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(HangarOptimizer, self).__init__()
        self.__state = _HangarOptimizerStates.DISABLED

    def enable(self):
        if self.__state == _HangarOptimizerStates.DISABLED:
            self.__closeHangarViews()
            if isPlayerAccount() and self.__hangarSpace.spaceInited:
                BigWorld.worldDrawEnabled(False)
                AnimationSequence.setEnableAnimationSequenceUpdate(False)
                WebBrowser.pauseExternalCache(True)
            self.__state = _HangarOptimizerStates.ENABLED

    def disable(self, needShowHangar=True):
        if self.isEnabled and needShowHangar:
            showHangar()
            app = self.__appFactory.getApp()
            if app:
                app.containerManager.onViewLoaded += self.__onViewLoaded
            if isPlayerAccount() and self.__hangarSpace.spaceInited:
                BigWorld.worldDrawEnabled(True)
            self.__state = _HangarOptimizerStates.DISABLING
        elif self.isEnabled and not needShowHangar:
            if isPlayerAccount() and self.__hangarSpace.spaceInited:
                BigWorld.worldDrawEnabled(True)
                AnimationSequence.setEnableAnimationSequenceUpdate(True)
                WebBrowser.pauseExternalCache(False)
            self.__state = _HangarOptimizerStates.DISABLED

    def clear(self):
        if self.__state == _HangarOptimizerStates.DISABLING:
            app = self.__appFactory.getApp()
            if app:
                app.containerManager.onViewLoaded -= self.__onViewLoaded
        if self.__state in (_HangarOptimizerStates.ENABLED, _HangarOptimizerStates.DISABLING) and isPlayerAccount() and self.__hangarSpace.spaceInited:
            BigWorld.worldDrawEnabled(True)
            AnimationSequence.setEnableAnimationSequenceUpdate(True)
            WebBrowser.pauseExternalCache(False)
        self.__state = _HangarOptimizerStates.DISABLED

    @property
    def isEnabled(self):
        return self.__state == _HangarOptimizerStates.ENABLED

    def __closeHangarViews(self):
        windows = self.__gui.windowsManager.findWindows(lambda w: w.layer == WindowLayer.SUB_VIEW)
        if not windows:
            return
        window = windows[0]
        if isinstance(window, SFWindow) and window.content and window.content.alias == VIEW_ALIAS.LOBBY_HANGAR:
            window.destroy()

    def __onViewLoaded(self, view, *_):
        if view.alias == VIEW_ALIAS.LOBBY_HANGAR:
            if self.__state == _HangarOptimizerStates.DISABLING:
                AnimationSequence.setEnableAnimationSequenceUpdate(True)
                WebBrowser.pauseExternalCache(False)
                self.__state = _HangarOptimizerStates.DISABLED
            self.__appFactory.getApp().containerManager.onViewLoaded -= self.__onViewLoaded
