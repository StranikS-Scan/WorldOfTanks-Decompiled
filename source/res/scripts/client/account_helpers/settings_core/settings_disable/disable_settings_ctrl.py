# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/settings_disable/disable_settings_ctrl.py
from account_helpers.settings_core.settings_disable import aop as daop
from typing import TYPE_CHECKING
from debug_utils import LOG_WARNING
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, aop
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGameController
if TYPE_CHECKING:
    from typing import Optional, Set, Dict, Any, Iterable
    from account_helpers.settings_core import settings_storages

class DisableSettingsController(IGameController, IGlobalListener):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__userSettings = None
        self.__keyToValConfig = None
        self.__keyToGUIPath = None
        self.__storageKeysToDisable = None
        self.__disabledStorages = {}
        self._weaver = None
        self.__areSettingChanged = False
        return

    def init(self):
        self.__keyToValConfig = {}
        self.__keyToGUIPath = {}
        self.__storageKeysToDisable = set([])
        self.__disabledStorages = {}
        self._weaver = aop.Weaver()

    def fini(self):
        self.__settingsCore.onSettingsReady -= self.__swapAfter
        self.__clearWeaver()
        self._weaver = None
        self.__keyToValConfig = None
        self.__keyToGUIPath = None
        self.__storageKeysToDisable = None
        self.__userSettings = None
        self.__areSettingChanged = False
        return

    def registerRecord(self, name, value, storages, guiPath):
        for storage in storages:
            self.__storageKeysToDisable.add(storage)

        self.__keyToValConfig[name] = value
        self.__keyToGUIPath[name] = guiPath

    def onDisconnected(self):
        self.stopGlobalListening()
        self.__clearWeaver()
        if self.__userSettings is not None:
            self.__rollbackDisabledStorages()
            self.__settingsCore.clearStorages()
            self.__userSettings = None
        self.__areSettingChanged = False
        return

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
        if self._canBeApplied() == self.__areSettingChanged:
            return
        if self._canBeApplied():
            self._disable()
        else:
            self._enable()

    def __swapAfter(self):
        self.__settingsCore.onSettingsReady -= self.__swapAfter
        self.__swapSettings()

    def _disable(self):
        self.__userSettings = {setting:self.__settingsCore.getSetting(setting) for setting in self.__keyToValConfig}
        if self._weaver.findPointcut(daop.DisableCameraSettingsFlashPointcut) == -1:
            self._weaver.weave(pointcut=daop.DisableCameraSettingsFlashPointcut, settings=self.__keyToGUIPath)
            self.__disableStorages()
        self.__settingsCore.applySettings(self.__keyToValConfig)
        self.__areSettingChanged = True

    def _enable(self):
        self.__clearWeaver()
        if self.__userSettings is not None:
            self.__rollbackDisabledStorages()
            self.__settingsCore.applySettings(self.__userSettings)
            self.__userSettings = None
        self.__areSettingChanged = False
        return

    def __clearWeaver(self):
        if self._weaver is not None:
            self._weaver.clear()
        return

    def __disableStorages(self):
        for st in self.__storageKeysToDisable:
            settingsCoreSt = self.__settingsCore.storages
            if st in settingsCoreSt:
                self.__disabledStorages[st] = settingsCoreSt[st]
                del settingsCoreSt[st]
            LOG_WARNING('Provided setting is not in the storages list. {}'.format(st))

    def __rollbackDisabledStorages(self):
        settingsCoreSt = self.__settingsCore.storages
        for stK, stV in self.__disabledStorages.iteritems():
            if stK not in settingsCoreSt:
                settingsCoreSt[stK] = stV

        self.__disabledStorages = {}
