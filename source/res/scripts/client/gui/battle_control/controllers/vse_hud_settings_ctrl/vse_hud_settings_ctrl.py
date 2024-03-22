# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/vse_hud_settings_ctrl.py
import typing
from Event import Event, EventManager
from gui.battle_control.arena_info.interfaces import IVSEHUDSettingsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.ally_list import AllyListClientModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.battle_communication import BattleCommunicationModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.chat import ChatModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.enemy_list import EnemyListClientModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.minimap import MinimapClientModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.respawn_hud import RespawnHUDClientModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.countdown import CountdownClientModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.primary_objective import PrimaryObjectiveClientModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.progress_counter import ProgressCounterClientModel
from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.secondary_objective import SecondaryObjectiveClientModel
from pve_battle_hud import getPveHudLogger, WidgetType
_logger = getPveHudLogger()
SettingsTypes = typing.Union[AllyListClientModel, EnemyListClientModel, MinimapClientModel, CountdownClientModel, BattleCommunicationModel, ChatModel, RespawnHUDClientModel]
ItemSettingsTypes = typing.Union[ProgressCounterClientModel, PrimaryObjectiveClientModel, SecondaryObjectiveClientModel]

class VSEHUDSettingsController(IVSEHUDSettingsController):
    __slots__ = ('_settings', '_eManager', 'onSettingsChanged', 'onItemSettingsChanged')

    def __init__(self):
        super(VSEHUDSettingsController, self).__init__()
        self._settings = {}
        self._eManager = EventManager()
        self.onSettingsChanged = Event(self._eManager)
        self.onItemSettingsChanged = Event(self._eManager)

    def getControllerID(self):
        return BATTLE_CTRL_ID.VSE_HUD_SETTINGS_CTRL

    def startControl(self, *args):
        pass

    def stopControl(self):
        self._settings.clear()
        self._eManager.clear()

    def setSettings(self, settingsID, settings):
        _logger.debug('New pve hud settings: settingsID=%s settings=%s.', settingsID, settings)
        self._settings[settingsID] = settings
        self.onSettingsChanged(settingsID)

    def getSettings(self, settingsID):
        settings = self._settings.get(settingsID)
        if settings is None:
            _logger.debug('Settings for settingsID=%s not set.', settingsID)
            return
        else:
            return settings

    def setItemSettings(self, settingsID, itemID, settings):
        _logger.debug('New pve hud item settings: settingsID=%s itemID=%s settings=%s.', settingsID, itemID, settings)
        itemsSettings = self._settings.setdefault(settingsID, {})
        if itemID in itemsSettings:
            _logger.debug('Item settings for settingsID=%s itemID=%s already set.', settingsID, itemID)
        itemsSettings[itemID] = settings
        self.onItemSettingsChanged(settingsID, itemID)

    def getItemSettings(self, settingsID, itemID):
        itemsSettings = self._settings.get(settingsID)
        if itemsSettings is None:
            _logger.debug('Settings for settingsID=%s not set.', settingsID)
            return
        else:
            itemSetting = itemsSettings.get(itemID)
            if itemSetting is None:
                _logger.debug('Item settings for settingsID=%s itemID=%s not set.', settingsID, itemID)
                return
            return itemSetting
