# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ribbons_panel.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from helpers import i18n
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS, GRAPHICS
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.Scaleform.daapi.view.meta.RibbonsPanelMeta import RibbonsPanelMeta
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.battle_control import avatar_getter
from gui.battle_control import g_sessionProvider
_RIBBON_SOUNDS_ENABLED = True
_SHOW_RIBBON_SOUND_NAME = 'show_ribbon'
_HIDE_RIBBON_SOUND_NAME = 'hide_ribbon'
_CHANGE_RIBBON_SOUND_NAME = 'increment_ribbon_counter'
_SOUNDS = (_SHOW_RIBBON_SOUND_NAME, _HIDE_RIBBON_SOUND_NAME, _CHANGE_RIBBON_SOUND_NAME)
_EXTENDED_RENDER_PIPELINE = 0
_ADDITIONAL_USER_SETTINGS = (BATTLE_EVENTS.VEHICLE_INFO,
 BATTLE_EVENTS.EVENT_NAME,
 BATTLE_EVENTS.SHOW_IN_BATTLE,
 GRAPHICS.RENDER_PIPELINE)
_BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES = {BATTLE_EVENTS.ENEMY_HP_DAMAGE: _BET.DAMAGE,
 BATTLE_EVENTS.BLOCKED_DAMAGE: _BET.ARMOR,
 BATTLE_EVENTS.ENEMY_RAM_ATTACK: _BET.RAM,
 BATTLE_EVENTS.ENEMY_BURNING: _BET.BURN,
 BATTLE_EVENTS.ENEMY_KILL: _BET.DESTRUCTION,
 BATTLE_EVENTS.ENEMY_DETECTION: _BET.DETECTION,
 BATTLE_EVENTS.ENEMY_TRACK_DAMAGE: _BET.ASSIST_TRACK,
 BATTLE_EVENTS.ENEMY_DETECTION_DAMAGE: _BET.ASSIST_SPOT,
 BATTLE_EVENTS.ENEMY_CRITICAL_HIT: _BET.CRITS,
 BATTLE_EVENTS.BASE_CAPTURE: _BET.CAPTURE,
 BATTLE_EVENTS.BASE_CAPTURE_DROP: _BET.DEFENCE}

def _getVehicleData(arenaDP, vehArenaID):
    vTypeInfoVO = arenaDP.getVehicleInfo(vehArenaID).vehicleType
    vehicleClassTag = vTypeInfoVO.classTag or ''
    vehicleName = vTypeInfoVO.shortNameWithPrefix
    return (vehicleName, vehicleClassTag)


def _formatCounter(counter):
    return i18n.makeString(INGAME_GUI.COUNTRIBBONS_MULTISEPARATOR, multiplier=counter)


def _baseRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.CAPTURE or BATTLE_EFFICIENCY_TYPES.DEFENCE ribbon.
    :param ribbon: An instance of _BaseRibbon derived class.
    :param updater: Reference to view update method.
    """
    updater(ribbonType=ribbon.getType(), leftFieldStr=str(ribbon.getPoints()))


def _enemyDetectionRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.DETECTION ribbon.
    :param ribbon: An instance of _EnemyDetectionRibbon class.
    :param updater: Reference to view update method.
    """
    updater(ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(ribbon.getCount()))


def _singleVehDamageRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.ARMOR or BATTLE_EFFICIENCY_TYPES.DAMAGE ribbon.
    :param ribbon: An instance of _SingleVehicleDamageRibbon derived class.
    :param updater: Reference to view update method.
    """
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    updater(ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=BigWorld.wg_getIntegralFormat(ribbon.getDamage()))


def _multiVehHitRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.CRITS ribbon.
    :param ribbon: An instance of _MultiVehicleHitRibbon derived class.
    :param updater: Reference to view update method.
    """
    vehIDs = ribbon.getVehIDs()
    count = len(vehIDs)
    assert count > 0
    if count > 1:
        updater(ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(ribbon.getExtraSum()), rightFieldStr=_formatCounter(count))
    else:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, vehIDs[0])
        updater(ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(ribbon.getExtraSum()), vehName=vehicleName, vehType=vehicleClassTag)


def _multiVehDamageRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show  BATTLE_EFFICIENCY_TYPES.RAM, BATTLE_EFFICIENCY_TYPES.BURN,
    BATTLE_EFFICIENCY_TYPES.ASSIST_TRACK or  BATTLE_EFFICIENCY_TYPES.ASSIST_SPOT ribbon.
    :param ribbon: An instance of _MultiVehicleDamageRibbon derived class.
    :param updater: Reference to view update method.
    """
    vehIDs = ribbon.getVehIDs()
    count = len(vehIDs)
    assert count > 0
    if count > 1:
        updater(ribbonType=ribbon.getType(), leftFieldStr=str(ribbon.getExtraSum()), rightFieldStr=_formatCounter(count))
    else:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, vehIDs[0])
        updater(ribbonType=ribbon.getType(), leftFieldStr=str(ribbon.getExtraSum()), vehName=vehicleName, vehType=vehicleClassTag)


def _killRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show  BATTLE_EFFICIENCY_TYPES.DESTRUCTION ribbon.
    :param ribbon: An instance of _EnemyKillRibbon class.
    :param updater: Reference to view update method.
    """
    vehIDs = ribbon.getVehIDs()
    count = len(vehIDs)
    assert count > 0
    if count > 1:
        updater(ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(count))
    else:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, vehIDs[0])
        updater(ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag)


_RIBBONS_FMTS = {_BET.CAPTURE: _baseRibbonFormatter,
 _BET.DEFENCE: _baseRibbonFormatter,
 _BET.DETECTION: _enemyDetectionRibbonFormatter,
 _BET.ARMOR: _singleVehDamageRibbonFormatter,
 _BET.DAMAGE: _singleVehDamageRibbonFormatter,
 _BET.CRITS: _multiVehHitRibbonFormatter,
 _BET.RAM: _multiVehDamageRibbonFormatter,
 _BET.BURN: _multiVehDamageRibbonFormatter,
 _BET.ASSIST_TRACK: _multiVehDamageRibbonFormatter,
 _BET.ASSIST_SPOT: _multiVehDamageRibbonFormatter,
 _BET.DESTRUCTION: _killRibbonFormatter}
_AGGREGATED_RIBBON_TYPES = (_BET.CAPTURE,)

class BattleRibbonsPanel(RibbonsPanelMeta):

    def __init__(self):
        super(BattleRibbonsPanel, self).__init__()
        self.__enabled = True
        self.__userPreferences = {}
        self.__isWithRibbonName = True
        self.__isWithVehName = True
        self.__isExtendedAnim = True
        self.__isVisible = True
        self.__arenaDP = g_sessionProvider.getCtx().getArenaDP()
        self.__ribbonsAggregator = RibbonsAggregator()
        self.__ribbonsAggregator.onRibbonAdded += self.__showRibbon
        self.__ribbonsAggregator.onRibbonUpdated += self.__showRibbon

    def onShow(self):
        self.__playSound(_SHOW_RIBBON_SOUND_NAME)

    def onChange(self):
        self.__playSound(_CHANGE_RIBBON_SOUND_NAME)

    def onHide(self, ribbonType):
        LOG_DEBUG_DEV('RIBBON PANEL: onHide: ribbonType="{}"'.format(ribbonType))
        if ribbonType not in _AGGREGATED_RIBBON_TYPES:
            self.__ribbonsAggregator.clearRibbonData(ribbonType)
        self.__playSound(_HIDE_RIBBON_SOUND_NAME)

    def _populate(self):
        super(BattleRibbonsPanel, self)._populate()
        self.__enabled = bool(g_settingsCore.getSetting(BATTLE_EVENTS.SHOW_IN_BATTLE)) and self.__arenaDP is not None
        self.__isWithRibbonName = bool(g_settingsCore.getSetting(BATTLE_EVENTS.EVENT_NAME))
        self.__isWithVehName = bool(g_settingsCore.getSetting(BATTLE_EVENTS.VEHICLE_INFO))
        self.__isExtendedAnim = g_settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == _EXTENDED_RENDER_PIPELINE
        for settingName in _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES:
            key = _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES[settingName]
            self.__userPreferences[key] = bool(g_settingsCore.getSetting(settingName))

        self.__setupView()
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__onGUIVisibilityChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        if self.__enabled:
            self.__ribbonsAggregator.start()
        return

    def _dispose(self):
        self.__ribbonsAggregator.onRibbonAdded -= self.__showRibbon
        self.__ribbonsAggregator.onRibbonUpdated -= self.__showRibbon
        g_eventBus.removeListener(GameEvent.GUI_VISIBILITY, self.__onGUIVisibilityChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        if self.__enabled:
            self.__ribbonsAggregator.stop()
        self.__arenaDP = None
        super(BattleRibbonsPanel, self)._dispose()
        return

    def __playSound(self, eventName):
        if not self.__isVisible or not _RIBBON_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play') and hasattr(soundNotifications, 'isPlaying'):
            for eventName in _SOUNDS:
                if soundNotifications.isPlaying(eventName):
                    break
            else:
                soundNotifications.play(eventName)

    def __addBattleEfficiencyEvent(self, ribbonType='', leftFieldStr='', vehName='', vehType='', rightFieldStr=''):
        LOG_DEBUG_DEV('RIBBON PANEL: __addBattleEfficiencyEvent: ribbonType="{}", leftFieldStr="{}", vehName="{}", vehType="{}", rightFieldStr="{}".'.format(ribbonType, leftFieldStr, vehName, vehType, rightFieldStr))
        self.as_addBattleEfficiencyEventS(ribbonType, leftFieldStr, vehName, vehType, rightFieldStr)

    def __showRibbon(self, ribbon):
        if self.__checkUserPreferences(ribbon) and ribbon.getType() in _RIBBONS_FMTS:
            updater = _RIBBONS_FMTS[ribbon.getType()]
            updater(ribbon, self.__arenaDP, self.__addBattleEfficiencyEvent)

    def __onGUIVisibilityChanged(self, event):
        self.__isVisible = event.ctx['visible']

    def __onSettingsChanged(self, diff):
        addSettings = {}
        for item in diff:
            if item in _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES:
                key = _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES[item]
                self.__userPreferences[key] = bool(diff[item])
            if item in _ADDITIONAL_USER_SETTINGS:
                addSettings[item] = diff[item]

        if addSettings:
            enabled = bool(addSettings.get(BATTLE_EVENTS.SHOW_IN_BATTLE, self.__enabled)) and self.__arenaDP is not None
            self.__isWithRibbonName = bool(g_settingsCore.getSetting(BATTLE_EVENTS.EVENT_NAME))
            self.__isWithVehName = bool(g_settingsCore.getSetting(BATTLE_EVENTS.VEHICLE_INFO))
            self.__isExtendedAnim = g_settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == _EXTENDED_RENDER_PIPELINE
            if self.__enabled != enabled:
                self.__enabled = enabled
                if self.__enabled:
                    self.__ribbonsAggregator.start()
                else:
                    self.__ribbonsAggregator.stop()
            self.as_setSettingsS(self.__enabled, self.__isExtendedAnim, self.__isWithRibbonName, self.__isWithVehName)
        return

    def __checkUserPreferences(self, ribbon):
        """
        Returns True if the user has enabled displaying of the given ribbon or there is no
        setting for the given ribbon. Otherwise returns False.
        :param ribbon: An instance of _Ribbon derived class.
        """
        return self.__userPreferences.get(ribbon.getType(), True)

    def __setupView(self):
        self.as_setupS([[_BET.ARMOR, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.ARMOR))],
         [_BET.DEFENCE, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.DEFENCE))],
         [_BET.DAMAGE, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.DAMAGE))],
         [_BET.ASSIST_SPOT, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.ASSIST_SPOT))],
         [_BET.ASSIST_TRACK, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.ASSIST_TRACK))],
         [_BET.BURN, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.BURN))],
         [_BET.CAPTURE, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.CAPTURE))],
         [_BET.DESTRUCTION, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.DESTRUCTION))],
         [_BET.DETECTION, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.DETECTION))],
         [_BET.RAM, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.RAM))],
         [_BET.CRITS, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.CRITS))]], self.__isExtendedAnim, self.__enabled, self.__isWithRibbonName, self.__isWithVehName)
