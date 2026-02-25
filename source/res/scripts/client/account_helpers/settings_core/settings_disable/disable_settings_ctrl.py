# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/settings_disable/disable_settings_ctrl.py
from account_helpers.settings_core.settings_disable import aop as daop
from typing import TYPE_CHECKING
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, aop
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGameController
if TYPE_CHECKING:
    from typing import Optional, Set, Dict, Any, Iterable

class DisableSettingsController(IGameController, IGlobalListener):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__keyToValConfig = None
        self.__keyToGUIPath = None
        self.__storageKeysToDisable = None
        self._weaver = None
        self.__areSettingChanged = False
        return

    def init(self):
        self.__keyToValConfig = {}
        self.__keyToGUIPath = {}
        self.__storageKeysToDisable = set([])
        self._weaver = aop.Weaver()

    def fini(self):
        self.__settingsCore.onSettingsReady -= self.__swapAfter
        self.__clearWeaver()
        self._weaver = None
        self.__keyToValConfig = None
        self.__keyToGUIPath = None
        self.__storageKeysToDisable = None
        self.__areSettingChanged = False
        return

    def registerRecord(self, name, value, storages, guiPath, disable=True):
        for storage in storages:
            self.__storageKeysToDisable.add(storage)

        self.__keyToValConfig[name] = value
        if disable:
            self.__keyToGUIPath[name] = guiPath

    def onDisconnected(self):
        self.stopGlobalListening()
        if self.__areSettingChanged:
            self._enable()

    def onAvatarBecomePlayer(self):
        self.stopGlobalListening()
        self.__swapSettings()

    def onLobbyInited(self, event):
        self.__swapSettings()
        self.startGlobalListening()

    def onPrbEntitySwitched(self):
        self.__swapSettings()

    def _canBeApplied(self):
        raise NotImplementedError

    def __swapSettings(self):
        if not self.__settingsCore.isReady:
            self.__settingsCore.onSettingsReady += self.__swapAfter
            return
        canBeApplied = self._canBeApplied()
        if canBeApplied == self.__areSettingChanged:
            return
        if canBeApplied:
            self._disable()
        else:
            self._enable()

    def __swapAfter(self):
        self.__settingsCore.onSettingsReady -= self.__swapAfter
        self.__swapSettings()

    def _disable(self):
        self.__settingsCore.setOverrideSettings(self.__keyToValConfig, self.__storageKeysToDisable)
        if self._weaver.findPointcut(daop.DisableCameraSettingsFlashPointcut) == -1:
            self._weaver.weave(pointcut=daop.DisableCameraSettingsFlashPointcut, settings=self.__keyToGUIPath)
        self.__areSettingChanged = True

    def _enable(self):
        self.__clearWeaver()
        self.__settingsCore.unsetOverrideSettings()
        self.__areSettingChanged = False

    def __clearWeaver(self):
        if self._weaver is not None:
            self._weaver.clear()
        return
