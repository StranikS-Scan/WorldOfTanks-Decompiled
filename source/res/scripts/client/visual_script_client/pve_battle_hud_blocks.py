# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/pve_battle_hud_blocks.py
from pve_battle_hud import getPveHudLogger, WidgetType
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.dependency import dependencyImporter
from visual_script_client.pve_common import ClientBattleHUDWidgetSettings, PropertySlotSpec, SettingType
settings = dependencyImporter('gui.battle_control.controllers.vse_hud_settings_ctrl.settings')
_logger = getPveHudLogger()

class SetProgressCounterSettings(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.progress_counter.ProgressCounterClientModel
    _WIDGET_TYPE = WidgetType.PROGRESS_COUNTER
    _SETTING_TYPE = SettingType.ITEM
    _SETTINGS_CONFIG = [PropertySlotSpec('header', SLOT_TYPE.STR, required=True), PropertySlotSpec('icon', SLOT_TYPE.STR, editorData=['shield', 'swords', 'wave'], required=True)]


class SetEnemyListSettings(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.enemy_list.EnemyListClientModel
    _WIDGET_TYPE = WidgetType.ENEMY_LIST
    _SETTING_TYPE = SettingType.GENERAL
    _SETTINGS_CONFIG = [PropertySlotSpec('showSpottedIcon', SLOT_TYPE.BOOL, defaultValue=True), PropertySlotSpec('highlightElite', SLOT_TYPE.BOOL, defaultValue=False)]


class SetPrimaryObjectiveSettings(ClientBattleHUDWidgetSettings):
    _ICONS = ['flagFailure', 'flagSuccess']
    _SETTINGS_MODEL = settings.primary_objective.PrimaryObjectiveClientModel
    _WIDGET_TYPE = WidgetType.PRIMARY_OBJECTIVE
    _SETTING_TYPE = SettingType.ITEM
    _SETTINGS_CONFIG = [PropertySlotSpec('header', SLOT_TYPE.STR),
     PropertySlotSpec('subheader', SLOT_TYPE.STR),
     PropertySlotSpec('startSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('remindTimers', arrayOf(SLOT_TYPE.INT)),
     PropertySlotSpec('remindSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('countdownTimer', SLOT_TYPE.INT),
     PropertySlotSpec('countdownSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('success', SLOT_TYPE.STR),
     PropertySlotSpec('successIcon', SLOT_TYPE.STR, editorData=_ICONS),
     PropertySlotSpec('successSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('failure', SLOT_TYPE.STR),
     PropertySlotSpec('failureIcon', SLOT_TYPE.STR, editorData=_ICONS),
     PropertySlotSpec('failureSound', SLOT_TYPE.SOUND)]


class SetSecondaryObjectiveSettings(ClientBattleHUDWidgetSettings):
    _ICONS = ['icon_info', 'icon_quest', 'icon_win']
    _SETTINGS_MODEL = settings.secondary_objective.SecondaryObjectiveClientModel
    _WIDGET_TYPE = WidgetType.SECONDARY_OBJECTIVE
    _SETTING_TYPE = SettingType.ITEM
    _SETTINGS_CONFIG = [PropertySlotSpec('header', SLOT_TYPE.STR),
     PropertySlotSpec('subheader', SLOT_TYPE.STR),
     PropertySlotSpec('startSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('icon', SLOT_TYPE.STR, editorData=_ICONS),
     PropertySlotSpec('countdownTimer', SLOT_TYPE.INT),
     PropertySlotSpec('countdownSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('successSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('failureSound', SLOT_TYPE.SOUND)]


class SetAllyListSettings(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.ally_list.AllyListClientModel
    _WIDGET_TYPE = WidgetType.ALLY_LIST
    _SETTING_TYPE = SettingType.GENERAL
    _SETTINGS_CONFIG = [PropertySlotSpec('showFrags', SLOT_TYPE.BOOL, defaultValue=True), PropertySlotSpec('showVehicleTypeIcon', SLOT_TYPE.BOOL, defaultValue=False), PropertySlotSpec('highlightElite', SLOT_TYPE.BOOL, defaultValue=False)]


class SetMinimapSettings(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.minimap.MinimapClientModel
    _WIDGET_TYPE = WidgetType.MINIMAP
    _SETTING_TYPE = SettingType.GENERAL
    _SETTINGS_CONFIG = [PropertySlotSpec('showGrid', SLOT_TYPE.BOOL),
     PropertySlotSpec('canToggleFullMap', SLOT_TYPE.BOOL),
     PropertySlotSpec('minimumAnimationDuration', SLOT_TYPE.FLOAT, defaultValue=0.3),
     PropertySlotSpec('maximumAnimationDuration', SLOT_TYPE.FLOAT, defaultValue=0.9),
     PropertySlotSpec('animationDurationPerMeter', SLOT_TYPE.FLOAT, defaultValue=0.0005),
     PropertySlotSpec('minimumAnimationDistance', SLOT_TYPE.FLOAT, defaultValue=10.0)]


class SetPrebattleCountdownSettings(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.countdown.CountdownClientModel
    _WIDGET_TYPE = WidgetType.COUNTDOWN
    _SETTING_TYPE = SettingType.GENERAL
    _SETTINGS_CONFIG = [PropertySlotSpec('header', SLOT_TYPE.STR, required=True), PropertySlotSpec('subheader', SLOT_TYPE.STR), PropertySlotSpec('battleStartMessage', SLOT_TYPE.STR, required=True)]


class SetChatSettings(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.chat.ChatModel
    _WIDGET_TYPE = WidgetType.CHAT
    _SETTING_TYPE = SettingType.GENERAL
    _SETTINGS_CONFIG = [PropertySlotSpec('hide', SLOT_TYPE.BOOL, defaultValue=False)]


class SetBattleCommunicationsSettings(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.battle_communication.BattleCommunicationModel
    _WIDGET_TYPE = WidgetType.BATTLE_COMMUNICATION
    _SETTING_TYPE = SettingType.GENERAL
    _SETTINGS_CONFIG = [PropertySlotSpec('hide', SLOT_TYPE.BOOL, defaultValue=False)]


class SetRespawnHUDSetting(ClientBattleHUDWidgetSettings):
    _SETTINGS_MODEL = settings.respawn_hud.RespawnHUDClientModel
    _WIDGET_TYPE = WidgetType.RESPAWN_HUD
    _SETTING_TYPE = SettingType.GENERAL
    _SETTINGS_CONFIG = [PropertySlotSpec('showLivesInAlliesList', SLOT_TYPE.BOOL),
     PropertySlotSpec('showLivesInTankPanel', SLOT_TYPE.BOOL),
     PropertySlotSpec('dynamicRespawnHeader', SLOT_TYPE.STR),
     PropertySlotSpec('dynamicRespawnSubheader', SLOT_TYPE.STR),
     PropertySlotSpec('dynamicRespawnSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('staticRespawnHeader', SLOT_TYPE.STR),
     PropertySlotSpec('staticRespawnSubheader', SLOT_TYPE.STR),
     PropertySlotSpec('staticRespawnSound', SLOT_TYPE.SOUND),
     PropertySlotSpec('battleOverHeader', SLOT_TYPE.STR),
     PropertySlotSpec('battleOverSubheader', SLOT_TYPE.STR),
     PropertySlotSpec('battleOverSound', SLOT_TYPE.SOUND)]
