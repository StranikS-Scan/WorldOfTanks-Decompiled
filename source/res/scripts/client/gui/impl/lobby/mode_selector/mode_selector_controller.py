# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/mode_selector_controller.py
from constants import Configs
from gui.impl.lobby.mode_selector.items.items_constants import COLUMN_SETTINGS, modeNamesByArenaBonusType
from helpers.server_settings import ModeSelectorConfig
from skeletons.gui.game_control import IModeSelectorController
from skeletons.gui.lobby_context import ILobbyContext
from helpers import dependency, server_settings

class ModeSelectorController(IModeSelectorController):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().modeSelectorConfig

    def getColumnSettings(self):
        return self.getModeSettings().columnSettings

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._updateSettings(COLUMN_SETTINGS)

    def onAccountBecomeNonPlayer(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def fini(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    @server_settings.serverSettingsChangeListener(Configs.MODE_SELECTOR_CONFIG.value)
    def __onServerSettingsChange(self, diff):
        if diff['mode_selector_config']:
            self._updateSettings(COLUMN_SETTINGS)
        elif COLUMN_SETTINGS:
            COLUMN_SETTINGS.clear()

    @staticmethod
    def convertConfigKeysFromArenaBonusType(config):
        return {modeNamesByArenaBonusType.get(k):v for k, v in config.columnSettings.iteritems()}

    def _updateSettings(self, settings):
        config = self.getModeSettings()
        if config.isValid():
            settings.update(self.convertConfigKeysFromArenaBonusType(config))
