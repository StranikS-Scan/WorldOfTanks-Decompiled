# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/UiEffectsManager.py
from account_helpers.settings_core.settings_constants import GRAPHICS
from frameworks.wulf import WindowLayer, WindowStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader

class UiEffectsManager(object):
    gui = dependency.descriptor(IGuiLoader)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__hangarIsVisible = False
        self.app = None
        return

    def populate(self, app):
        self.app = app
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__updateUIEffectSettingsChanged()

    def dispose(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.gui.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        self.gui.windowsManager.onWindowStatusChanged -= self.__onViewStatusChanged
        self.app = None
        return

    def __updateUIEffectSettingsChanged(self):
        hasUIEffects = self.settingsCore.getSetting(GRAPHICS.UI_EFFECTS)
        if hasUIEffects:
            self.gui.windowsManager.onViewStatusChanged += self.__onViewStatusChanged
            self.gui.windowsManager.onWindowStatusChanged += self.__onViewStatusChanged
            self.__updateUIEffectOptimization()
        else:
            self.gui.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
            self.gui.windowsManager.onWindowStatusChanged -= self.__onViewStatusChanged
            self.app.graphicsOptimizationManager.switchOptimizationEnabled(True)

    def __onViewStatusChanged(self, _, newStatus):
        hasUIEffects = self.settingsCore.getSetting(GRAPHICS.UI_EFFECTS)
        if not hasUIEffects or newStatus not in (WindowStatus.LOADED, WindowStatus.DESTROYED):
            return
        self.__updateUIEffectOptimization()

    def __updateUIEffectOptimization(self):
        hasHangar = self.app.containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_HANGAR}) is not None
        hasTopSubView = self.gui.windowsManager.findWindows(lambda w: w.layer == WindowLayer.TOP_SUB_VIEW)
        hangarIsVisible = hasHangar and not hasTopSubView
        if self.__hangarIsVisible != hangarIsVisible:
            self.__hangarIsVisible = hangarIsVisible
            g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.HANGAR_STATUS_CHANGED, ctx={'isVisible': hangarIsVisible}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.app.graphicsOptimizationManager.switchOptimizationEnabled(not self.__hangarIsVisible)
        return

    def __onSettingsChanged(self, diff):
        if GRAPHICS.UI_EFFECTS in diff:
            self.__updateUIEffectSettingsChanged()
