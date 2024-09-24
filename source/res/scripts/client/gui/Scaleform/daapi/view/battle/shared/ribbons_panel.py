# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ribbons_panel.py
import logging
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS, GRAPHICS
from gui.Scaleform.daapi.view.battle.shared import ribbons_aggregator
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import DAMAGE_SOURCE
from gui.Scaleform.daapi.view.meta.RibbonsPanelMeta import RibbonsPanelMeta
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
from gui.battle_control import avatar_getter
from constants import VEHICLE_BUNKER_TURRET_TAG
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE
from gui.battle_control.battle_constants import BonusRibbonLabel as _BRL, VEHICLE_VIEW_STATE_ID_TO_WEATHER_ZONE_NAME
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from items import tankmen
from items.battle_royale import isSpawnedBot, isBattleRoyale
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_RIBBON_SOUNDS_ENABLED = True
_SHOW_RIBBON_SOUND_NAME = 'show_ribbon'
_SHOW_RIBBON_EXP_SOUND_NAME = 'show_ribbon_role_exp'
_HIDE_RIBBON_SOUND_NAME = 'hide_ribbon'
_CHANGE_RIBBON_SOUND_NAME = 'increment_ribbon_counter'
_SOUNDS = (_SHOW_RIBBON_SOUND_NAME, _HIDE_RIBBON_SOUND_NAME, _CHANGE_RIBBON_SOUND_NAME)
_EXTENDED_RENDER_PIPELINE = 0
_ADDITIONAL_USER_SETTINGS = (BATTLE_EVENTS.VEHICLE_INFO,
 BATTLE_EVENTS.EVENT_NAME,
 BATTLE_EVENTS.SHOW_IN_BATTLE,
 GRAPHICS.RENDER_PIPELINE,
 GRAPHICS.COLOR_BLIND)
_BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES = {BATTLE_EVENTS.ENEMY_HP_DAMAGE: (_BET.DAMAGE,
                                 _BET.SPAWNED_BOT_DMG,
                                 _BET.DAMAGE_BY_MINEFIELD,
                                 _BET.DEALT_DMG_BY_CORRODING_SHOT,
                                 _BET.DEALT_DMG_BY_FIRE_CIRCLE,
                                 _BET.DEALT_DMG_BY_CLING_BRANDER,
                                 _BET.DAMAGE_BY_AIRSTRIKE,
                                 _BET.DAMAGE_BY_ARTILLERY),
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
                                 _BET.RECEIVED_WORLD_COLLISION,
                                 _BET.BERSERKER,
                                 _BET.RECEIVED_DMG_BY_SPAWNED_BOT,
                                 _BET.RECEIVED_BY_MINEFIELD,
                                 _BET.RECEIVED_BY_SMOKE,
                                 _BET.RECEIVED_BY_CORRODING_SHOT,
                                 _BET.RECEIVED_BY_FIRE_CIRCLE,
                                 _BET.RECEIVED_BY_CLING_BRANDER,
                                 _BET.RECEIVED_BY_AIRSTRIKE,
                                 _BET.RECEIVED_BY_ARTILLERY,
                                 _BET.RECEIVED_BY_DEATH_ZONE,
                                 _BET.MINEFIELD_ZONE,
                                 _BET.DEATH_ZONE,
                                 _BET.STATIC_DEATH_ZONE,
                                 _BET.FIRE_DAMAGE_ZONE),
 BATTLE_EVENTS.RECEIVED_CRITS: (_BET.RECEIVED_CRITS,),
 BATTLE_EVENTS.ENEMIES_STUN: (_BET.STUN,),
 BATTLE_EVENTS.ENEMY_ASSIST_STUN: (_BET.ASSIST_STUN,),
 BATTLE_EVENTS.CREW_PERKS: (_BET.PERK,)}

def _getVehicleData(arenaDP, vehArenaID):
    vInfo = arenaDP.getVehicleInfo(vehArenaID)
    vTypeInfoVO = vInfo.vehicleType
    vehicleClassTag = vInfo.getDisplayedClassTag() if vTypeInfoVO.classTag else ''
    vehicleName = vInfo.getDisplayedName()
    if isBattleRoyale(vTypeInfoVO.tags) and isSpawnedBot(vTypeInfoVO.tags):
        vehicleClassTag = ''
    if VEHICLE_BUNKER_TURRET_TAG in vTypeInfoVO.tags:
        vehicleClassTag = VEHICLE_BUNKER_TURRET_TAG
    return (vehicleName, vehicleClassTag)


def _formatCounter(counter):
    return backport.text(R.strings.ingame_gui.countRibbons.multiSeparator(), multiplier=counter)


def _baseRibbonFormatter(ribbon, arenaDP, updater):
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=str(ribbon.getPoints()))


def _perkRibbonFormatter(ribbon, arenaDP, updater):
    perkID = ribbon.getPerkID()
    skillName = tankmen.getSkillsConfig().vsePerkToSkill.get(perkID)
    rightFieldStr = R.strings.crew_perks.dyn(skillName).name
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=skillName, rightFieldStr=backport.text(rightFieldStr()))


def _weatherZoneRibbonFormatter(ribbon, arenaDP, updater):
    zoneID = ribbon.getWeatherZoneID()
    zoneName = VEHICLE_VIEW_STATE_ID_TO_WEATHER_ZONE_NAME[zoneID]
    rightFieldStr = R.strings.ingame_gui.efficiencyRibbons.dyn(zoneName)
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=zoneName, rightFieldStr=backport.text(rightFieldStr()))


def _enemyDetectionRibbonFormatter(ribbon, arenaDP, updater):
    count = ribbon.getTargetsAmount()
    bonusRibbonLabelID = _BRL.BASE_BONUS_LABEL if ribbon.isRoleBonus() else _BRL.NO_BONUS
    if count > 1:
        updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(count), bonusRibbonLabelID=bonusRibbonLabelID, role=ribbon.role())
    else:
        vIDs = ribbon.getVehIDs()
        if vIDs:
            vehicleName, vehicleClassTag = _getVehicleData(arenaDP, vIDs[0])
        else:
            _logger.error('Enemy detection ribbon has no vehicle ID! %s', ribbon.getID())
            vehicleName = ''
            vehicleClassTag = ''
        updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, bonusRibbonLabelID=bonusRibbonLabelID, role=ribbon.role())


def _enemiesStunRibbonFormatter(ribbon, arenaDP, updater):
    count = ribbon.getTargetsAmount()
    bonusRibbonLabelID = _BRL.BASE_BONUS_LABEL if ribbon.isRoleBonus() else _BRL.NO_BONUS
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(count), bonusRibbonLabelID=bonusRibbonLabelID, role=ribbon.role())


def _singleVehRibbonFormatter(ribbon, arenaDP, updater):
    if ribbon.getDamageSource() == DAMAGE_SOURCE.PLAYER:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    else:
        vehicleName, vehicleClassTag = '', ribbon.getDamageSource()
    bonusRibbonLabelID = _BRL.BASE_BONUS_LABEL if ribbon.isRoleBonus() else _BRL.NO_BONUS
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=backport.getIntegralFormat(ribbon.getExtraValue()), bonusRibbonLabelID=bonusRibbonLabelID, role=ribbon.role())


def _receivedRamRibbonFormatter(ribbon, arenaDP, updater):
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    if arenaDP.getPlayerVehicleID() == ribbon.getVehicleID():
        vehicleName = ''
        vehicleClassTag = ''
    bonusRibbonLabelID = _BRL.BASE_BONUS_LABEL if ribbon.isRoleBonus() else _BRL.NO_BONUS
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=backport.getIntegralFormat(ribbon.getExtraValue()), bonusRibbonLabelID=bonusRibbonLabelID, role=ribbon.role())


def _criticalHitRibbonFormatter(ribbon, arenaDP, updater):
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=_formatCounter(ribbon.getExtraValue()))


def _receivedCriticalHitRibbonFormatter(ribbon, arenaDP, updater):
    if ribbon.getDamageSource() == DAMAGE_SOURCE.PLAYER:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    else:
        vehicleName, vehicleClassTag = '', ribbon.getDamageSource()
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=_formatCounter(ribbon.getExtraValue()))


def _killRibbonFormatter(ribbon, arenaDP, updater):
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    value = ribbon.getExtraValue()
    leftFieldStr = backport.getIntegralFormat(value) if value else ''
    bonusRibbonLabelID = _BRL.BASE_BONUS_LABEL if ribbon.isRoleBonus() else _BRL.NO_BONUS
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=leftFieldStr, bonusRibbonLabelID=bonusRibbonLabelID, role=ribbon.role())


def _epicEventRibbonFormatter(ribbon, arenaDP, updater):
    value = ribbon.getExtraValue()
    leftFieldStr = backport.getIntegralFormat(value) if value else ''
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=leftFieldStr)


def _healthAddedFormatter(ribbon, arenaDP, updater):
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=backport.getIntegralFormat(ribbon.getExtraValue()))


_RIBBONS_FMTS = {_BET.CAPTURE: _baseRibbonFormatter,
 _BET.DEFENCE: _baseRibbonFormatter,
 _BET.DETECTION: _enemyDetectionRibbonFormatter,
 _BET.STUN: _enemiesStunRibbonFormatter,
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
 _BET.ASSIST_STUN: _singleVehRibbonFormatter,
 _BET.VEHICLE_RECOVERY: _epicEventRibbonFormatter,
 _BET.ENEMY_SECTOR_CAPTURED: _epicEventRibbonFormatter,
 _BET.DESTRUCTIBLE_DAMAGED: _epicEventRibbonFormatter,
 _BET.DESTRUCTIBLE_DESTROYED: _epicEventRibbonFormatter,
 _BET.DESTRUCTIBLES_DEFENDED: _epicEventRibbonFormatter,
 _BET.DEFENDER_BONUS: _epicEventRibbonFormatter,
 _BET.BASE_CAPTURE_BLOCKED: _baseRibbonFormatter,
 _BET.ASSIST_BY_ABILITY: _singleVehRibbonFormatter,
 _BET.DEATH_ZONE: _singleVehRibbonFormatter,
 _BET.STATIC_DEATH_ZONE: _singleVehRibbonFormatter,
 _BET.MINEFIELD_ZONE: _singleVehRibbonFormatter,
 _BET.BERSERKER: _singleVehRibbonFormatter,
 _BET.SPAWNED_BOT_DMG: _singleVehRibbonFormatter,
 _BET.RECEIVED_DMG_BY_SPAWNED_BOT: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_MINEFIELD: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_MINEFIELD: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_ARTILLERY: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_ARTILLERY: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_AIRSTRIKE: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_AIRSTRIKE: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_DEATH_ZONE: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_SMOKE: _singleVehRibbonFormatter,
 _BET.DEALT_DMG_BY_CORRODING_SHOT: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_CORRODING_SHOT: _singleVehRibbonFormatter,
 _BET.DEALT_DMG_BY_FIRE_CIRCLE: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_FIRE_CIRCLE: _singleVehRibbonFormatter,
 _BET.DEALT_DMG_BY_CLING_BRANDER: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_CLING_BRANDER: _singleVehRibbonFormatter,
 _BET.DEALT_DMG_BY_THUNDER_STRIKE: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_THUNDER_STRIKE: _singleVehRibbonFormatter,
 _BET.VEHICLE_HEALTH_ADDED: _healthAddedFormatter,
 _BET.PERK: _perkRibbonFormatter,
 _BET.DAMAGE_BY_BATTLESHIP: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_DESTROYER: _singleVehRibbonFormatter,
 _BET.WEATHER_ZONE: _weatherZoneRibbonFormatter,
 _BET.FIRE_DAMAGE_ZONE: _singleVehRibbonFormatter}
_DISPLAY_PRECONDITIONS = {_BET.DETECTION: lambda dp, ribbon: dp.getVehicleInfo(ribbon.getVehIDs()[0]).vehicleType.compactDescr > 0}

class BattleRibbonsPanel(RibbonsPanelMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ribbonsAggregator=None):
        super(BattleRibbonsPanel, self).__init__()
        self.__enabled = True
        self.__userPreferences = {}
        self.__isWithRibbonName = True
        self.__isWithVehName = True
        self.__isExtendedAnim = True
        self.__isVisible = True
        self.__arenaDP = self.sessionProvider.getCtx().getArenaDP()
        self._ribbonsAggregator = ribbonsAggregator or ribbons_aggregator.createRibbonsAggregator()
        self.__delayedRibbons = []

    @property
    def userPreferences(self):
        return self.__userPreferences

    def onShow(self, ribbonID):
        sound = _SHOW_RIBBON_SOUND_NAME
        ribbon = self._ribbonsAggregator.getRibbon(ribbonID)
        if ribbon and ribbon.isRoleBonus():
            sound = _SHOW_RIBBON_EXP_SOUND_NAME
        self.__playSound(sound)

    def onChange(self):
        self.__playSound(_CHANGE_RIBBON_SOUND_NAME)

    def onHide(self, ribbonID):
        ribbon = self._ribbonsAggregator.getRibbon(ribbonID)
        _logger.debug('RIBBON PANEL: onHide: ribbonID=%s, ribbon="%s"', ribbonID, ribbon)
        if ribbon is not None:
            self._ribbonsAggregator.resetRibbonData(ribbonID)
            self.__playSound(_HIDE_RIBBON_SOUND_NAME)
        return

    def getCtrlScope(self):
        return ARENA_LISTENER_SCOPE.VEHICLES

    def addVehicleInfo(self, vo, _):
        self.__processDelayedRibbons()

    def updateVehiclesInfo(self, updated, _):
        self.__processDelayedRibbons()

    def _populate(self):
        super(BattleRibbonsPanel, self)._populate()
        self.__enabled = bool(self.settingsCore.getSetting(BATTLE_EVENTS.SHOW_IN_BATTLE)) and self.__arenaDP is not None
        self.__isWithRibbonName = bool(self.settingsCore.getSetting(BATTLE_EVENTS.EVENT_NAME))
        self.__isWithVehName = bool(self.settingsCore.getSetting(BATTLE_EVENTS.VEHICLE_INFO))
        self.__isExtendedAnim = self.settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE) == _EXTENDED_RENDER_PIPELINE
        for settingName in _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES:
            self.__setUserPrefference(settingName, bool(self.settingsCore.getSetting(settingName)))

        self.__setupView()
        self.settingsCore.onSettingsChanged += self._onSettingsChanged
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__onGUIVisibilityChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self._ribbonsAggregator.onRibbonAdded += self.__onRibbonAdded
        self._ribbonsAggregator.onRibbonUpdated += self.__onRibbonUpdated
        self._ribbonsAggregator.start()
        if not self.__enabled:
            self._ribbonsAggregator.suspend()
        self.sessionProvider.addArenaCtrl(self)
        return

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        self.__delayedRibbons = []
        self._ribbonsAggregator.onRibbonAdded -= self.__onRibbonAdded
        self._ribbonsAggregator.onRibbonUpdated -= self.__onRibbonUpdated
        g_eventBus.removeListener(GameEvent.GUI_VISIBILITY, self.__onGUIVisibilityChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged
        self._ribbonsAggregator.stop()
        self.__arenaDP = None
        self.as_resetS()
        super(BattleRibbonsPanel, self)._dispose()
        return

    def _shouldShowRibbon(self, ribbon):
        return self.__checkUserPreferences(ribbon) and self.__checkControllingOwnVehicle()

    def _getRibbonFormatter(self, ribbon):
        return ribbon.getFormatter() or _RIBBONS_FMTS.get(ribbon.getType())

    def _onSettingsChanged(self, diff):
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
                    self._ribbonsAggregator.resume()
                else:
                    self._ribbonsAggregator.suspend()
            self.as_setSettingsS(self.__enabled, self.__isExtendedAnim, self.__isWithRibbonName, self.__isWithVehName)
        return

    def __processDelayedRibbons(self):
        for ribbon, method in ((self._ribbonsAggregator.getRibbon(ribbonID), method) for ribbonID, method in self.__delayedRibbons):
            if self.__canBeShown(ribbon):
                self.__invalidateRibbon(ribbon, method)
                self.__delayedRibbons.remove((ribbon.getID(), method))

    def __playSound(self, eventName):
        if not self.__isVisible or not _RIBBON_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play') and hasattr(soundNotifications, 'isPlaying'):
            for soundName in _SOUNDS:
                if soundNotifications.isPlaying(soundName):
                    break
            else:
                soundNotifications.play(eventName)

    def __onRibbonAdded(self, ribbon):
        self.__invalidateRibbon(ribbon, self.__addRibbon)

    def __onRibbonUpdated(self, ribbon):
        self.__invalidateRibbon(ribbon, self.__updateRibbon)

    def __invalidateRibbon(self, ribbon, method):
        if not self.__canBeShown(ribbon):
            _logger.debug('Delaying ribbon processing %s', ribbon)
            self.__delayedRibbons.append((ribbon.getID(), method))
            return
        if self._shouldShowRibbon(ribbon):
            ribbonType = ribbon.getType()
            updater = self._getRibbonFormatter(ribbon)
            if updater:
                updater(ribbon, self.__arenaDP, method)
            else:
                _logger.error('Could not find formatter for ribbon type %s', ribbonType)
        else:
            self._ribbonsAggregator.resetRibbonData(ribbon.getID())

    def __addRibbon(self, ribbonID, ribbonType='', leftFieldStr='', vehName='', vehType='', rightFieldStr='', bonusRibbonLabelID=_BRL.NO_BONUS, role=''):
        _logger.debug('RIBBON PANEL: as_addBattleEfficiencyEventS: ribbonID=%s, ribbonType="%s", ", leftFieldStr="%s, vehName="%s", vehType="%s", rightFieldStr="%s", bonusRibbonLabelID=%s, role=%s.', ribbonID, ribbonType, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)
        self.as_addBattleEfficiencyEventS(ribbonType, ribbonID, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)

    def __updateRibbon(self, ribbonID, ribbonType='', leftFieldStr='', vehName='', vehType='', rightFieldStr='', bonusRibbonLabelID=_BRL.NO_BONUS, role=''):
        _logger.debug('RIBBON PANEL: as_updateBattleEfficiencyEventS: ribbonID=%s, ribbonType="%s", ", leftFieldStr="%s, vehName="%s", vehType="%s", rightFieldStr="%s", bonusRibbonLabelID=%s, role=%s.', ribbonID, ribbonType, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)
        self.as_updateBattleEfficiencyEventS(ribbonType, ribbonID, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)

    def __canBeShown(self, ribbon):
        ribbonType = ribbon.getType()
        displayPrecondition = _DISPLAY_PRECONDITIONS.get(ribbonType)
        return False if displayPrecondition and not displayPrecondition(self.__arenaDP, ribbon) else True

    def __onGUIVisibilityChanged(self, event):
        self.__isVisible = event.ctx['visible']

    def __setUserPrefference(self, settingName, value):
        ribbonTypes = _BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES[settingName]
        for rType in ribbonTypes:
            self.__userPreferences[rType] = value

    def __checkUserPreferences(self, ribbon):
        return self.__userPreferences.get(ribbon.getType(), True)

    def __checkControllingOwnVehicle(self):
        return avatar_getter.getPlayerVehicleID() == self.sessionProvider.shared.vehicleState.getControllingVehicleID()

    def _getRibbonsConfig(self):
        return [[_BET.ARMOR, backport.text(R.strings.ingame_gui.efficiencyRibbons.armor())],
         [_BET.DEFENCE, backport.text(R.strings.ingame_gui.efficiencyRibbons.defence())],
         [_BET.DAMAGE, backport.text(R.strings.ingame_gui.efficiencyRibbons.damage())],
         [_BET.ASSIST_SPOT, backport.text(R.strings.ingame_gui.efficiencyRibbons.assistSpot())],
         [_BET.ASSIST_TRACK, backport.text(R.strings.ingame_gui.efficiencyRibbons.assistTrack())],
         [_BET.BURN, backport.text(R.strings.ingame_gui.efficiencyRibbons.burn())],
         [_BET.CAPTURE, backport.text(R.strings.ingame_gui.efficiencyRibbons.capture())],
         [_BET.DESTRUCTION, backport.text(R.strings.ingame_gui.efficiencyRibbons.kill())],
         [_BET.DETECTION, backport.text(R.strings.ingame_gui.efficiencyRibbons.spotted())],
         [_BET.RAM, backport.text(R.strings.ingame_gui.efficiencyRibbons.ram())],
         [_BET.CRITS, backport.text(R.strings.ingame_gui.efficiencyRibbons.crits())],
         [_BET.WORLD_COLLISION, backport.text(R.strings.ingame_gui.efficiencyRibbons.worldCollision())],
         [_BET.RECEIVED_CRITS, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedCrits())],
         [_BET.RECEIVED_DAMAGE, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedDamage())],
         [_BET.RECEIVED_BURN, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedBurn())],
         [_BET.RECEIVED_RAM, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedRam())],
         [_BET.RECEIVED_WORLD_COLLISION, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedWorldCollision())],
         [_BET.STUN, backport.text(R.strings.ingame_gui.efficiencyRibbons.stun())],
         [_BET.ASSIST_STUN, backport.text(R.strings.ingame_gui.efficiencyRibbons.assistStun())],
         [_BET.VEHICLE_RECOVERY, backport.text(R.strings.ingame_gui.efficiencyRibbons.vehicleRecovery())],
         [_BET.ENEMY_SECTOR_CAPTURED, backport.text(R.strings.ingame_gui.efficiencyRibbons.enemySectorCaptured())],
         [_BET.DESTRUCTIBLE_DAMAGED, backport.text(R.strings.ingame_gui.efficiencyRibbons.destructibleDamaged())],
         [_BET.DESTRUCTIBLE_DESTROYED, backport.text(R.strings.ingame_gui.efficiencyRibbons.destructibleDestroyed())],
         [_BET.DESTRUCTIBLES_DEFENDED, backport.text(R.strings.ingame_gui.efficiencyRibbons.destructiblesDefended())],
         [_BET.DEFENDER_BONUS, backport.text(R.strings.ingame_gui.efficiencyRibbons.defenderBonus())],
         [_BET.BASE_CAPTURE_BLOCKED, backport.text(R.strings.ingame_gui.efficiencyRibbons.defence())],
         [_BET.ASSIST_BY_ABILITY, backport.text(R.strings.ingame_gui.efficiencyRibbons.assistByAbility())],
         [_BET.DEATH_ZONE, backport.text(R.strings.ingame_gui.efficiencyRibbons.deathZone())],
         [_BET.STATIC_DEATH_ZONE, backport.text(R.strings.ingame_gui.efficiencyRibbons.staticDeathZone())],
         [_BET.MINEFIELD_ZONE, backport.text(R.strings.ingame_gui.efficiencyRibbons.minefieldZone())],
         [_BET.BERSERKER, backport.text(R.strings.ingame_gui.efficiencyRibbons.berserker())],
         [_BET.SPAWNED_BOT_DMG, backport.text(R.strings.ingame_gui.efficiencyRibbons.spawnedBotDmg())],
         [_BET.RECEIVED_DMG_BY_SPAWNED_BOT, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedDmgBySpawnedBot())],
         [_BET.DAMAGE_BY_MINEFIELD, backport.text(R.strings.ingame_gui.efficiencyRibbons.damageByMinefield())],
         [_BET.RECEIVED_BY_MINEFIELD, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedByMinefield())],
         [_BET.DAMAGE_BY_ARTILLERY, backport.text(R.strings.ingame_gui.efficiencyRibbons.ArtilleryDmg())],
         [_BET.RECEIVED_BY_ARTILLERY, backport.text(R.strings.ingame_gui.efficiencyRibbons.ArtilleryDmg())],
         [_BET.DAMAGE_BY_AIRSTRIKE, backport.text(R.strings.ingame_gui.efficiencyRibbons.AirstrikeDmg())],
         [_BET.RECEIVED_BY_AIRSTRIKE, backport.text(R.strings.ingame_gui.efficiencyRibbons.AirstrikeDmg())],
         [_BET.RECEIVED_BY_DEATH_ZONE, backport.text(R.strings.ingame_gui.efficiencyRibbons.CannonDmg())],
         [_BET.RECEIVED_BY_SMOKE, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedBySmoke())],
         [_BET.DEALT_DMG_BY_CORRODING_SHOT, backport.text(R.strings.ingame_gui.efficiencyRibbons.dealtDamageByCorrodingShot())],
         [_BET.RECEIVED_BY_CORRODING_SHOT, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedByCorrodingShot())],
         [_BET.DEALT_DMG_BY_FIRE_CIRCLE, backport.text(R.strings.ingame_gui.efficiencyRibbons.dealtDamageByFireCircle())],
         [_BET.RECEIVED_BY_FIRE_CIRCLE, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedByFireCircle())],
         [_BET.DEALT_DMG_BY_CLING_BRANDER, backport.text(R.strings.ingame_gui.efficiencyRibbons.dealtDamageByClingBrander())],
         [_BET.RECEIVED_BY_CLING_BRANDER, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedByClingBrander())],
         [_BET.DEALT_DMG_BY_THUNDER_STRIKE, backport.text(R.strings.ingame_gui.efficiencyRibbons.dealtDamageByThunderStrike())],
         [_BET.RECEIVED_BY_THUNDER_STRIKE, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedByThunderStrike())],
         [_BET.VEHICLE_HEALTH_ADDED, backport.text(R.strings.ingame_gui.efficiencyRibbons.healthAdded())],
         [_BET.DAMAGE_BY_BATTLESHIP, backport.text(R.strings.ingame_gui.efficiencyRibbons.damageByBattleship())],
         [_BET.DAMAGE_BY_DESTROYER, backport.text(R.strings.ingame_gui.efficiencyRibbons.damageByDestroyer())],
         [_BET.PERK, ''],
         [_BET.WEATHER_ZONE, ''],
         [_BET.FIRE_DAMAGE_ZONE, backport.text(R.strings.ingame_gui.efficiencyRibbons.fireDamageZone())]]

    def __setupView(self):
        ribbonsCfg = self._getRibbonsConfig()
        self.as_setupS(ribbonsCfg, self.__isExtendedAnim, self.__enabled, self.__isWithRibbonName, self.__isWithVehName, [backport.text(R.strings.ingame_gui.efficiencyRibbons.bonusRibbon())])
