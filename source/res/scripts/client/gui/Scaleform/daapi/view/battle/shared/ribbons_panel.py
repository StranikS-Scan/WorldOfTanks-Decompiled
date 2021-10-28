# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ribbons_panel.py
import logging
import BigWorld
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS, GRAPHICS
from gui.battle_control.battle_constants import BonusRibbonLabel as _BRL
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared import ribbons_aggregator
from gui.Scaleform.daapi.view.meta.RibbonsPanelMeta import RibbonsPanelMeta
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
from gui.battle_control import avatar_getter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import DAMAGE_SOURCE
from items.battle_royale import isSpawnedBot, isBattleRoyale
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
_BATTLE_EVENTS_SETTINGS_TO_BATTLE_EFFICIENCY_TYPES = {BATTLE_EVENTS.ENEMY_HP_DAMAGE: (_BET.DAMAGE, _BET.SPAWNED_BOT_DMG, _BET.DAMAGE_BY_MINEFIELD),
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
                                 _BET.EVENT_DEATH_ON_PHASE_CHANGE),
 BATTLE_EVENTS.RECEIVED_CRITS: (_BET.RECEIVED_CRITS,),
 BATTLE_EVENTS.ENEMIES_STUN: (_BET.STUN,),
 BATTLE_EVENTS.ENEMY_ASSIST_STUN: (_BET.ASSIST_STUN,)}

def _getVehicleData(arenaDP, vehArenaID):
    player = BigWorld.player()
    botRole = player.getBotRole(vehArenaID)
    vTypeInfoVO = arenaDP.getVehicleInfo(vehArenaID).vehicleType
    vehicleClassTag = botRole or vTypeInfoVO.classTag or ''
    vehicleName = vTypeInfoVO.shortNameWithPrefix
    if isBattleRoyale(vTypeInfoVO.tags) and isSpawnedBot(vTypeInfoVO.tags):
        vehicleClassTag = ''
    return (vehicleName, vehicleClassTag)


def _formatCounter(counter):
    return backport.text(R.strings.ingame_gui.countRibbons.multiSeparator(), multiplier=counter)


def _baseRibbonFormatter(ribbon, arenaDP, updater):
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=str(ribbon.getPoints()))


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
            _logger.error('Enemy detection ribbon has no vehicle ID! %s', ribbon)
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


def _eventBuffEffectApplied(ribbon, arenaDP, updater):
    if ribbon.hasEffectValue:
        leftFieldStr = ''
        if ribbon.effectValue > 0:
            leftFieldStr = backport.text(R.strings.event.efficiencyRibbons.plus()) + backport.getIntegralFormat(ribbon.effectValue)
        vehName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.victimID)
    else:
        leftFieldStr = backport.text(R.strings.event.efficiencyRibbons.got_buff())
        vehName = backport.text(R.strings.event.efficiencyRibbons.dyn(ribbon.buffName).descr())
        vehicleClassTag = ''
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=leftFieldStr, vehName=vehName, vehType=vehicleClassTag)


def _eventActionApplied(ribbon, arenaDP, updater):
    leftFieldStr = backport.text(R.strings.event.efficiencyRibbons.plus())
    leftFieldStr += backport.getIntegralFormat(ribbon.actionValue)
    vehName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.victimID)
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=leftFieldStr, vehName=vehName, vehType=vehicleClassTag)


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
 _BET.EVENT_DEATH_ON_PHASE_CHANGE: _singleVehRibbonFormatter,
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
 _BET.BERSERKER: _singleVehRibbonFormatter,
 _BET.SPAWNED_BOT_DMG: _singleVehRibbonFormatter,
 _BET.RECEIVED_DMG_BY_SPAWNED_BOT: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_MINEFIELD: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_MINEFIELD: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_SMOKE: _singleVehRibbonFormatter,
 _BET.EVENT_HEAL_UP: _eventActionApplied,
 _BET.EVENT_ADD_AMMO: _eventActionApplied}
_BUFF_RIBBONS_FMTS = {_BET.BUFFS_RATION: _eventBuffEffectApplied,
 _BET.BUFFS_FUEL: _eventBuffEffectApplied,
 _BET.BUFFS_RATE_FIRE: _eventBuffEffectApplied,
 _BET.BUFFS_CONVERSION_SPEED: _eventBuffEffectApplied,
 _BET.BUFFS_INCREASED_MAXIMUM_DAMAGE: _eventBuffEffectApplied,
 _BET.BUFFS_DOUBLE_DAMAGE: _eventBuffEffectApplied,
 _BET.BUFFS_INCENDIARY_SHOT: _eventBuffEffectApplied,
 _BET.BUFFS_VAMPIRIC_SHOT: _eventBuffEffectApplied,
 _BET.BUFFS_CONSTANT_HP_REGENERATION: _eventBuffEffectApplied,
 _BET.BUFFS_ARMOR: _eventBuffEffectApplied}
_RIBBONS_FMTS.update(_BUFF_RIBBONS_FMTS)

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

    def onShow(self, ribbonID):
        sound = _SHOW_RIBBON_SOUND_NAME
        ribbon = self.__ribbonsAggregator.getRibbon(ribbonID)
        if ribbon and ribbon.isRoleBonus():
            sound = _SHOW_RIBBON_EXP_SOUND_NAME
        self.__playSound(sound)

    def onChange(self):
        self.__playSound(_CHANGE_RIBBON_SOUND_NAME)

    def onHide(self, ribbonID):
        ribbon = self.__ribbonsAggregator.getRibbon(ribbonID)
        _logger.debug('RIBBON PANEL: onHide: ribbonID=%s, ribbon="%s"', ribbonID, ribbon)
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
        isEventBattle = self.sessionProvider.arenaVisitor.gui.isEventBattle()
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__onGUIVisibilityChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__ribbonsAggregator.onRibbonAdded += self.__onRibbonAdded
        self.__ribbonsAggregator.onRibbonUpdated += self.__onRibbonUpdated
        self.__ribbonsAggregator.start()
        if not self.__enabled and not isEventBattle:
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
        return self._checkUserPreferences(ribbon)

    def _getRibbonsAggregator(self):
        return self.__ribbonsAggregator

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

    def _addRibbon(self, ribbonID, ribbonType='', leftFieldStr='', vehName='', vehType='', rightFieldStr='', bonusRibbonLabelID=_BRL.NO_BONUS, role=''):
        _logger.debug('RIBBON PANEL: as_addBattleEfficiencyEventS: ribbonID=%s, ribbonType="%s", ", leftFieldStr="%s, vehName="%s", vehType="%s", rightFieldStr="%s", bonusRibbonLabelID=%s, role=%s.', ribbonID, ribbonType, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)
        self.as_addBattleEfficiencyEventS(ribbonType, ribbonID, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)

    def _updateRibbon(self, ribbonID, ribbonType='', leftFieldStr='', vehName='', vehType='', rightFieldStr='', bonusRibbonLabelID=_BRL.NO_BONUS, role=''):
        _logger.debug('RIBBON PANEL: as_updateBattleEfficiencyEventS: ribbonID=%s, ribbonType="%s", ", leftFieldStr="%s, vehName="%s", vehType="%s", rightFieldStr="%s", bonusRibbonLabelID=%s, role=%s.', ribbonID, ribbonType, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)
        self.as_updateBattleEfficiencyEventS(ribbonType, ribbonID, leftFieldStr, vehName, vehType, rightFieldStr, bonusRibbonLabelID, role)

    def __onRibbonAdded(self, ribbon):
        self._invalidateRibbon(ribbon, self._addRibbon)

    def __onRibbonUpdated(self, ribbon):
        self._invalidateRibbon(ribbon, self._updateRibbon)

    def _invalidateRibbon(self, ribbon, method):
        if self._shouldShowRibbon(ribbon):
            if ribbon.getType() in _RIBBONS_FMTS:
                updater = _RIBBONS_FMTS[ribbon.getType()]
                updater(ribbon, self.__arenaDP, method)
            else:
                _logger.error('Could not find formatter for ribbon %s', ribbon)
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
            self.as_setSettingsS(self.__isPanelEnabled(), self.__isExtendedAnim, self.__isWithRibbonName, self.__isWithVehName)
        return

    def _checkUserPreferences(self, ribbon):
        return self.__userPreferences.get(ribbon.getType(), True) and self.__enabled

    def __isPanelEnabled(self):
        return self.sessionProvider.arenaVisitor.gui.isEventBattle() or self.__enabled

    def __setupView(self):
        ribbons = [[_BET.ARMOR, backport.text(R.strings.ingame_gui.efficiencyRibbons.armor())],
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
         [_BET.EVENT_DEATH_ON_PHASE_CHANGE, backport.text(R.strings.ingame_gui.efficiencyRibbons.eventDeathOnPhaseChange())],
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
         [_BET.BERSERKER, backport.text(R.strings.ingame_gui.efficiencyRibbons.berserker())],
         [_BET.SPAWNED_BOT_DMG, backport.text(R.strings.ingame_gui.efficiencyRibbons.spawnedBotDmg())],
         [_BET.RECEIVED_DMG_BY_SPAWNED_BOT, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedDmgBySpawnedBot())],
         [_BET.DAMAGE_BY_MINEFIELD, backport.text(R.strings.ingame_gui.efficiencyRibbons.damageByMinefield())],
         [_BET.RECEIVED_BY_MINEFIELD, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedByMinefield())],
         [_BET.RECEIVED_BY_SMOKE, backport.text(R.strings.ingame_gui.efficiencyRibbons.receivedBySmoke())]]
        if self.sessionProvider.arenaVisitor.gui.isEventBattle():
            ribbons.extend([[_BET.BUFFS_RATION, backport.text(R.strings.event.efficiencyRibbons.ration.title())],
             [_BET.BUFFS_FUEL, backport.text(R.strings.event.efficiencyRibbons.fuel.title())],
             [_BET.BUFFS_RATE_FIRE, backport.text(R.strings.event.efficiencyRibbons.multiplyGunReloadTime.title())],
             [_BET.BUFFS_CONVERSION_SPEED, backport.text(R.strings.event.efficiencyRibbons.multiplyShotDispersion.title())],
             [_BET.BUFFS_INCREASED_MAXIMUM_DAMAGE, backport.text(R.strings.event.efficiencyRibbons.multiplyDamageBy10.title())],
             [_BET.BUFFS_DOUBLE_DAMAGE, backport.text(R.strings.event.efficiencyRibbons.damageOnceOnShot.title())],
             [_BET.BUFFS_INCENDIARY_SHOT, backport.text(R.strings.event.efficiencyRibbons.igniteOnShot.title())],
             [_BET.BUFFS_VAMPIRIC_SHOT, backport.text(R.strings.event.efficiencyRibbons.healOnceOnShot.title())],
             [_BET.BUFFS_CONSTANT_HP_REGENERATION, backport.text(R.strings.event.efficiencyRibbons.regenerationHP.title())],
             [_BET.BUFFS_ARMOR, backport.text(R.strings.event.efficiencyRibbons.armor.title())],
             [_BET.EVENT_HEAL_UP, backport.text(R.strings.event.efficiencyRibbons.eventHealUp.title())],
             [_BET.EVENT_ADD_AMMO, backport.text(R.strings.event.efficiencyRibbons.eventAddAmmo.title())]])
        self.as_setupS(ribbons, self.__isExtendedAnim, self.__isPanelEnabled(), self.__isWithRibbonName, self.__isWithVehName, [backport.text(R.strings.ingame_gui.efficiencyRibbons.bonusRibbon())])
