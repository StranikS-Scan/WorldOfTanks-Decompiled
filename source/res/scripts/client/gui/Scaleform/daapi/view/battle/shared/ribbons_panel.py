# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ribbons_panel.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV, LOG_UNEXPECTED
from helpers import dependency
from helpers import i18n
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS, GRAPHICS
from gui.Scaleform.daapi.view.meta.RibbonsPanelMeta import RibbonsPanelMeta
from gui.Scaleform.daapi.view.battle.shared import ribbons_aggregator
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.battle_control import avatar_getter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_RIBBON_SOUNDS_ENABLED = True
_SHOW_RIBBON_SOUND_NAME = 'show_ribbon'
_HIDE_RIBBON_SOUND_NAME = 'hide_ribbon'
_CHANGE_RIBBON_SOUND_NAME = 'increment_ribbon_counter'
_SOUNDS = (_SHOW_RIBBON_SOUND_NAME, _HIDE_RIBBON_SOUND_NAME, _CHANGE_RIBBON_SOUND_NAME)
_EXTENDED_RENDER_PIPELINE = 0
_ADDITIONAL_USER_SETTINGS = (BATTLE_EVENTS.VEHICLE_INFO,
 BATTLE_EVENTS.EVENT_NAME,
 BATTLE_EVENTS.SHOW_IN_BATTLE,
 GRAPHICS.RENDER_PIPELINE,
 GRAPHICS.COLOR_BLIND)
_BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES = {BATTLE_EVENTS.ENEMY_HP_DAMAGE: (_BET.DAMAGE,),
 BATTLE_EVENTS.BLOCKED_DAMAGE: (_BET.ARMOR,),
 BATTLE_EVENTS.ENEMY_RAM_ATTACK: (_BET.RAM,),
 BATTLE_EVENTS.ENEMY_BURNING: (_BET.BURN,),
 BATTLE_EVENTS.ENEMY_WORLD_COLLISION: (_BET.WORLD_COLLISION,),
 BATTLE_EVENTS.ENEMY_KILL: (_BET.DESTRUCTION,),
 BATTLE_EVENTS.ENEMY_DETECTION: (_BET.DETECTION,),
 BATTLE_EVENTS.ENEMY_TRACK_DAMAGE: (_BET.ASSIST_TRACK,),
 BATTLE_EVENTS.ENEMY_DETECTION_DAMAGE: (_BET.ASSIST_SPOT,),
 BATTLE_EVENTS.ENEMY_CRITICAL_HIT: (_BET.CRITS,),
 BATTLE_EVENTS.BASE_CAPTURE: (_BET.CAPTURE,),
 BATTLE_EVENTS.BASE_CAPTURE_DROP: (_BET.DEFENCE,),
 BATTLE_EVENTS.RECEIVED_DAMAGE: (_BET.RECEIVED_DAMAGE,
                                 _BET.RECEIVED_BURN,
                                 _BET.RECEIVED_RAM,
                                 _BET.RECEIVED_WORLD_COLLISION),
 BATTLE_EVENTS.RECEIVED_CRITS: (_BET.RECEIVED_CRITS,),
 BATTLE_EVENTS.ENEMY_ASSIST_STUN: (_BET.STUN,)}

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
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=str(ribbon.getPoints()))


def _enemyDetectionRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.DETECTION ribbon.
    
    :param ribbon: An instance of _EnemyDetectionRibbon class.
    :param updater: Reference to view update method.
    """
    count = ribbon.getCount()
    if count > 1:
        updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(count))
    else:
        vIDs = ribbon.getVehIDs()
        if vIDs:
            vehicleName, vehicleClassTag = _getVehicleData(arenaDP, vIDs[0])
        else:
            LOG_UNEXPECTED('Enemy detection ribbon has no vehicle ID!', ribbon)
            vehicleName = ''
            vehicleClassTag = ''
        updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag)


def _singleVehRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.ARMOR or BATTLE_EFFICIENCY_TYPES.DAMAGE ribbon.
    :param ribbon: An instance of _SingleVehicleDamageRibbon derived class.
    :param updater: Reference to view update method.
    """
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=BigWorld.wg_getIntegralFormat(ribbon.getExtraValue()))


def _receivedRamRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show caused BATTLE_EFFICIENCY_TYPES.ARMOR.
    :param ribbon: An instance of _SingleVehicleDamageRibbon derived class.
    :param updater: Reference to view update method.
    """
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    if arenaDP.getPlayerVehicleID() == ribbon.getVehicleID():
        vehicleName = ''
        vehicleClassTag = ''
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=BigWorld.wg_getIntegralFormat(ribbon.getExtraValue()))


def _criticalHitRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.ARMOR or BATTLE_EFFICIENCY_TYPES.DAMAGE ribbon.
    :param ribbon: An instance of _SingleVehicleDamageRibbon derived class.
    :param updater: Reference to view update method.
    """
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=_formatCounter(ribbon.getExtraValue()))


def _receivedCriticalHitRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show BATTLE_EFFICIENCY_TYPES.ARMOR or BATTLE_EFFICIENCY_TYPES.DAMAGE ribbon.
    :param ribbon: An instance of _SingleVehicleDamageRibbon derived class.
    :param updater: Reference to view update method.
    """
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    if arenaDP.getPlayerVehicleID() == ribbon.getVehicleID():
        vehicleName = ''
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=_formatCounter(ribbon.getExtraValue()))


def _killRibbonFormatter(ribbon, arenaDP, updater):
    """
    Proxy to show  BATTLE_EFFICIENCY_TYPES.DESTRUCTION ribbon.
    :param ribbon: An instance of _EnemyKillRibbon class.
    :param updater: Reference to view update method.
    """
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    value = ribbon.getExtraValue()
    leftFieldStr = BigWorld.wg_getIntegralFormat(value) if value else ''
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=leftFieldStr)


_RIBBONS_FMTS = {_BET.CAPTURE: _baseRibbonFormatter,
 _BET.DEFENCE: _baseRibbonFormatter,
 _BET.DETECTION: _enemyDetectionRibbonFormatter,
 _BET.ARMOR: _singleVehRibbonFormatter,
 _BET.DAMAGE: _singleVehRibbonFormatter,
 _BET.CRITS: _criticalHitRibbonFormatter,
 _BET.RAM: _singleVehRibbonFormatter,
 _BET.BURN: _singleVehRibbonFormatter,
 _BET.WORLD_COLLISION: _singleVehRibbonFormatter,
 _BET.ASSIST_TRACK: _singleVehRibbonFormatter,
 _BET.ASSIST_SPOT: _singleVehRibbonFormatter,
 _BET.DESTRUCTION: _killRibbonFormatter,
 _BET.RECEIVED_DAMAGE: _singleVehRibbonFormatter,
 _BET.RECEIVED_CRITS: _receivedCriticalHitRibbonFormatter,
 _BET.RECEIVED_RAM: _receivedRamRibbonFormatter,
 _BET.RECEIVED_BURN: _singleVehRibbonFormatter,
 _BET.RECEIVED_WORLD_COLLISION: _singleVehRibbonFormatter,
 _BET.STUN: _singleVehRibbonFormatter}

class BattleRibbonsPanel(RibbonsPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(BattleRibbonsPanel, self).__init__()
        self.__enabled = True
        self.__userPreferences = {}
        self.__isWithRibbonName = True
        self.__isWithVehName = True
        self.__isExtendedAnim = True
        self.__isVisible = True
        self.__arenaDP = self.sessionProvider.getCtx().getArenaDP()
        self.__ribbonsAggregator = ribbons_aggregator.createRibbonsAggregator()
        self.__ribbonsAggregator.onRibbonAdded += self.__onRibbonAdded
        self.__ribbonsAggregator.onRibbonUpdated += self.__onRibbonUpdated

    def onShow(self):
        self.__playSound(_SHOW_RIBBON_SOUND_NAME)

    def onChange(self):
        self.__playSound(_CHANGE_RIBBON_SOUND_NAME)

    def onHide(self, ribbonID):
        ribbon = self.__ribbonsAggregator.getRibbon(ribbonID)
        LOG_DEBUG_DEV('RIBBON PANEL: onHide: ribbonID={}, ribbon="{}"'.format(ribbonID, ribbon))
        if ribbon is not None:
            self.__ribbonsAggregator.resetRibbonData(ribbonID)
            self.__playSound(_HIDE_RIBBON_SOUND_NAME)
        return

    def _populate(self):
        super(BattleRibbonsPanel, self)._populate()
        self.__enabled = bool(self.settingsCore.getSetting(BATTLE_EVENTS.SHOW_IN_BATTLE)) and self.__arenaDP is not None
        self.__isWithRibbonName = bool(self.settingsCore.getSetting(BATTLE_EVENTS.EVENT_NAME))
        self.__isWithVehName = bool(self.settingsCore.getSetting(BATTLE_EVENTS.VEHICLE_INFO))
        self.__isExtendedAnim = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == _EXTENDED_RENDER_PIPELINE
        for settingName in _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES:
            self.__setUserPrefference(settingName, bool(self.settingsCore.getSetting(settingName)))

        self.__setupView()
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__onGUIVisibilityChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__ribbonsAggregator.start()
        if not self.__enabled:
            self.__ribbonsAggregator.suspend()
        return

    def _dispose(self):
        self.__ribbonsAggregator.onRibbonAdded -= self.__onRibbonAdded
        self.__ribbonsAggregator.onRibbonUpdated -= self.__onRibbonUpdated
        g_eventBus.removeListener(GameEvent.GUI_VISIBILITY, self.__onGUIVisibilityChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__ribbonsAggregator.stop()
        self.__arenaDP = None
        self.as_resetS()
        super(BattleRibbonsPanel, self)._dispose()
        return

    def _shouldShowRibbon(self, ribbon):
        return self.__checkUserPreferences(ribbon)

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

    def _addRibbon(self, ribbonID, ribbonType='', leftFieldStr='', vehName='', vehType='', rightFieldStr=''):
        LOG_DEBUG_DEV('RIBBON PANEL: as_addBattleEfficiencyEventS: ribbonID={}, ribbonType="{}", ", leftFieldStr="{}, vehName="{}", vehType="{}", rightFieldStr="{}".'.format(ribbonID, ribbonType, leftFieldStr, vehName, vehType, rightFieldStr))
        self.as_addBattleEfficiencyEventS(ribbonType, ribbonID, leftFieldStr, vehName, vehType, rightFieldStr)

    def _updateRibbon(self, ribbonID, ribbonType='', leftFieldStr='', vehName='', vehType='', rightFieldStr=''):
        LOG_DEBUG_DEV('RIBBON PANEL: as_updateBattleEfficiencyEventS: ribbonID={}, ribbonType="{}", ", leftFieldStr="{}, vehName="{}", vehType="{}", rightFieldStr="{}".'.format(ribbonID, ribbonType, leftFieldStr, vehName, vehType, rightFieldStr))
        self.as_updateBattleEfficiencyEventS(ribbonType, ribbonID, leftFieldStr, vehName, vehType, rightFieldStr)

    def __onRibbonAdded(self, ribbon):
        self.__invalidateRibbon(ribbon, self._addRibbon)

    def __onRibbonUpdated(self, ribbon):
        self.__invalidateRibbon(ribbon, self._updateRibbon)

    def __invalidateRibbon(self, ribbon, method):
        if self._shouldShowRibbon(ribbon):
            if ribbon.getType() in _RIBBONS_FMTS:
                updater = _RIBBONS_FMTS[ribbon.getType()]
                updater(ribbon, self.__arenaDP, method)
            else:
                LOG_UNEXPECTED('Could not find formatter for ribbon ', ribbon)
        else:
            self.__ribbonsAggregator.resetRibbonData(ribbon.getID())

    def __onGUIVisibilityChanged(self, event):
        self.__isVisible = event.ctx['visible']

    def __setUserPrefference(self, settingName, value):
        ribbonTypes = _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES[settingName]
        for rType in ribbonTypes:
            self.__userPreferences[rType] = value

    def __onSettingsChanged(self, diff):
        addSettings = {}
        for item in diff:
            if item in _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES:
                self.__setUserPrefference(item, bool(diff[item]))
            if item in _ADDITIONAL_USER_SETTINGS:
                addSettings[item] = diff[item]

        if addSettings:
            enabled = bool(addSettings.get(BATTLE_EVENTS.SHOW_IN_BATTLE, self.__enabled)) and self.__arenaDP is not None
            self.__isWithRibbonName = bool(self.settingsCore.getSetting(BATTLE_EVENTS.EVENT_NAME))
            self.__isWithVehName = bool(self.settingsCore.getSetting(BATTLE_EVENTS.VEHICLE_INFO))
            self.__isExtendedAnim = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == _EXTENDED_RENDER_PIPELINE
            if self.__enabled != enabled:
                self.__enabled = enabled
                if self.__enabled:
                    self.__ribbonsAggregator.resume()
                else:
                    self.__ribbonsAggregator.suspend()
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
         [_BET.CRITS, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.CRITS))],
         [_BET.WORLD_COLLISION, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.WORLD_COLLISION))],
         [_BET.RECEIVED_CRITS, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.RECEIVED_CRITS))],
         [_BET.RECEIVED_DAMAGE, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.RECEIVED_DAMAGE))],
         [_BET.RECEIVED_BURN, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.RECEIVED_BURN))],
         [_BET.RECEIVED_RAM, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.RECEIVED_RAM))],
         [_BET.RECEIVED_WORLD_COLLISION, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.RECEIVED_WORLD_COLLISION))],
         [_BET.STUN, i18n.makeString(INGAME_GUI.efficiencyribbons(_BET.STUN))]], self.__isExtendedAnim, self.__enabled, self.__isWithRibbonName, self.__isWithVehName)
