# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/msgs_ctrl.py
import weakref
import math
import random
import BigWorld
from helpers import dependency
import BattleReplay
import Event
from ReplayEvents import g_replayEvents
from constants import ATTACK_REASON_INDICES as _AR_INDICES
from gui.battle_control.arena_info.arena_vos import EPIC_BATTLE_KEYS
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.battle_control import avatar_getter
from items.battle_royale import isSpawnedBot
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.sounds.r4_sound_constants import R4_SOUND

class _ENTITY_TYPE(object):
    UNKNOWN = 'unknown'
    SELF = 'self'
    ALLY = 'ally'
    ENEMY = 'enemy'
    SUICIDE = 'suicide'


_ATTACK_REASON_CODE = {_AR_INDICES['shot']: 'DEATH_FROM_SHOT',
 _AR_INDICES['fire']: 'DEATH_FROM_SHOT',
 _AR_INDICES['ramming']: 'DEATH_FROM_RAMMING',
 _AR_INDICES['world_collision']: 'DEATH_FROM_WORLD_COLLISION',
 _AR_INDICES['death_zone']: 'DEATH_FROM_DEATH_ZONE',
 _AR_INDICES['drowning']: 'DEATH_FROM_DROWNING',
 _AR_INDICES['overturn']: 'DEATH_FROM_OVERTURN',
 _AR_INDICES['artillery_protection']: 'DEATH_FROM_ARTILLERY_PROTECTION',
 _AR_INDICES['artillery_sector']: 'DEATH_FROM_SECTOR_PROTECTION',
 _AR_INDICES['bombers']: 'DEATH_FROM_SECTOR_BOMBERS',
 _AR_INDICES['recovery']: 'DEATH_FROM_RECOVERY',
 _AR_INDICES['artillery_eq']: 'DEATH_FROM_SHOT',
 _AR_INDICES['bomber_eq']: 'DEATH_FROM_SHOT',
 _AR_INDICES['minefield_eq']: 'DEATH_FROM_SHOT',
 _AR_INDICES['spawned_bot_explosion']: 'DEATH_FROM_SHOT',
 _AR_INDICES['supply_shot']: 'DEATH_FROM_SUPPLY_SHOT'}
_PLAYER_KILL_ENEMY_SOUND = 'enemy_killed_by_player'
_PLAYER_KILL_ALLY_SOUND = 'ally_killed_by_player'
_ALLY_KILLED_SOUND = 'ally_killed_by_enemy'
_ENEMY_KILLED_SOUND = 'enemy_killed_by_ally'

class BattleMessagesController(IBattleController):
    __slots__ = ('_battleCtx', '_arenaDP', '_arenaVisitor', '_eManager', '_buffer', '_isUIPopulated', 'onShowVehicleMessageByCode', 'onShowVehicleMessageByKey', 'onShowVehicleErrorByKey', 'onShowPlayerMessageByCode', 'onShowPlayerMessageByKey', 'onShowDestructibleEntityMessageByCode', '__weakref__')

    def __init__(self, setup):
        self._battleCtx = weakref.proxy(setup.battleCtx)
        self._arenaDP = weakref.proxy(setup.arenaDP)
        self._arenaVisitor = weakref.proxy(setup.arenaVisitor)
        self._eManager = Event.EventManager()
        self.onShowVehicleMessageByCode = Event.Event(self._eManager)
        self.onShowVehicleMessageByKey = Event.Event(self._eManager)
        self.onShowVehicleErrorByKey = Event.Event(self._eManager)
        self.onShowPlayerMessageByCode = Event.Event(self._eManager)
        self.onShowPlayerMessageByKey = Event.Event(self._eManager)
        self.onShowDestructibleEntityMessageByCode = Event.Event(self._eManager)
        self._buffer = []
        self._isUIPopulated = False

    def getControllerID(self):
        return BATTLE_CTRL_ID.MESSAGES

    def startControl(self):
        pass

    def stopControl(self):
        self._eManager.clear()
        self._battleCtx = None
        self._arenaDP = None
        self._arenaVisitor = None
        return

    def showDestructibleEntityDestroyedMessage(self, avatar, destructibleID, attackerID):
        try:
            playerVehicleID = avatar.playerVehicleID
        except AttributeError:
            return

        if attackerID == playerVehicleID:
            code = 'DESTRUCTIBLE_DESTROYED_SELF'
        elif BigWorld.player().team == 1:
            code = 'DESTRUCTIBLE_DESTROYED_ALLY'
        else:
            code = 'DESTRUCTIBLE_DESTROYED_ENEMY'
        self.onShowDestructibleEntityMessageByCode(code, destructibleID, attackerID)

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        try:
            playerVehicleID = avatar.playerVehicleID
        except AttributeError:
            return

        isMyVehicle = targetID == playerVehicleID
        if isMyVehicle:
            return
        elif targetID == attackerID and (self._battleCtx.isObserver(targetID) or self._battleCtx.isCommander(targetID)):
            return
        else:
            if not avatar.isVehicleAlive:
                if avatar.isObserver() and targetID == avatar.observedVehicleID:
                    return
                if targetID == avatar.inputHandler.ctrl.curVehicleID:
                    return
            code, postfix, sound, soundExt = self.__getKillInfo(avatar, targetID, attackerID, equipmentID, reason)
            if sound is not None:
                avatar.soundNotifications.play(sound)
            if soundExt is not None:
                avatar.soundNotifications.play(soundExt)
            self.onShowPlayerMessageByCode(code, postfix, targetID, attackerID, equipmentID)
            return

    def showVehicleDamageInfo(self, avatar, code, targetID, entityID, extra, equipmentID):
        code, postfix = self.__getDamageInfo(avatar, code, entityID, targetID)
        self.onShowPlayerMessageByCode(code, postfix, targetID, entityID, equipmentID)
        self.onShowVehicleMessageByCode(code, postfix, entityID, extra, equipmentID)

    def showVehicleMessage(self, key, args=None):
        self.onShowVehicleMessageByKey(key, args, None)
        return

    def showVehicleError(self, key, args=None):
        self.onShowVehicleErrorByKey(key, args, None)
        return

    def showVehicleSpawnMessage(self, team, name):
        key = 'SPAWN_ALLY' if BigWorld.player().team == team else 'SPAWN_ENEMY'
        self.onShowPlayerMessageByKey(key, {'entity': name})

    def showAllyHitMessage(self, vehicleID=None):
        self.onShowPlayerMessageByKey('ALLY_HIT', {'entity': self._battleCtx.getPlayerFullName(vID=vehicleID)}, (('entity', vehicleID),))

    def _getEntityString(self, avatar, entityID):
        if entityID == avatar.playerVehicleID:
            return _ENTITY_TYPE.SELF
        if self._battleCtx.isAlly(entityID):
            return _ENTITY_TYPE.ALLY
        return _ENTITY_TYPE.ENEMY if self._battleCtx.isEnemy(entityID) else _ENTITY_TYPE.UNKNOWN

    def __getDamageInfo(self, avatar, code, entityID, targetID):
        target = self._getEntityString(avatar, targetID)
        if not entityID or entityID == targetID:
            postfix = '%s_%s' % (target.upper(), _ENTITY_TYPE.SUICIDE.upper())
        else:
            entity = self._getEntityString(avatar, entityID)
            postfix = '%s_%s' % (entity.upper(), target.upper())
        return (code, postfix)

    def __getKillInfo(self, avatar, targetID, attackerID, equipmentID, reason):
        attacker = self._getEntityString(avatar, attackerID)
        target = _ENTITY_TYPE.SUICIDE
        if targetID != attackerID:
            target = self._getEntityString(avatar, targetID)
        code = _ATTACK_REASON_CODE.get(reason)
        sound = None
        soundExt = None
        if attackerID == BigWorld.player().playerVehicleID:
            if target == _ENTITY_TYPE.ENEMY:
                sound = _PLAYER_KILL_ENEMY_SOUND
            elif target == _ENTITY_TYPE.ALLY:
                sound = _PLAYER_KILL_ALLY_SOUND
                soundExt = _ALLY_KILLED_SOUND
        elif target == _ENTITY_TYPE.ALLY or target == _ENTITY_TYPE.SUICIDE and attacker == _ENTITY_TYPE.ALLY:
            soundExt = _ALLY_KILLED_SOUND
        elif target == _ENTITY_TYPE.ENEMY or target == _ENTITY_TYPE.SUICIDE and attacker == _ENTITY_TYPE.ENEMY:
            soundExt = _ENEMY_KILLED_SOUND
        return (code,
         '%s_%s' % (attacker.upper(), target.upper()),
         sound,
         soundExt)

    def onUIPopulated(self):
        self._isUIPopulated = True
        for args in self._buffer:
            self.onShowVehicleMessageByKey(*args)


class BattleMessagesPlayer(BattleMessagesController):

    def startControl(self):
        super(BattleMessagesPlayer, self).startControl()
        g_replayEvents.onWatcherNotify += self.__onWatcherNotify

    def stopControl(self):
        g_replayEvents.onWatcherNotify -= self.__onWatcherNotify
        super(BattleMessagesPlayer, self).stopControl()

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleKilledMessage(avatar, targetID, attackerID, equipmentID, reason)

    def showDestructibleEntityDestroyedMessage(self, avatar, destructibleID, attackerID):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showDestructibleEntityDestroyedMessage(avatar, destructibleID, attackerID)

    def showVehicleDamageInfo(self, avatar, code, targetID, entityID, extra, equipmentID):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleDamageInfo(avatar, code, targetID, entityID, extra, equipmentID)

    def showVehicleMessage(self, key, args=None):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleMessage(key, args)

    def showVehicleError(self, key, args=None):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleError(key, args)

    def showAllyHitMessage(self, vehicleID=None):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showAllyHitMessage(vehicleID)

    def showInfoMessage(self, key, withBuffer=False, args=None):
        if withBuffer and not self._isUIPopulated:
            self._buffer.append((key, args))
        else:
            super(BattleMessagesPlayer, self).showVehicleMessage(key, args)

    def __onWatcherNotify(self, message, args):
        self.showInfoMessage(message, withBuffer=True, args=args)


class EpicBattleMessagesPlayer(BattleMessagesPlayer):

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        if not self._messageIsAllowedInEpicBattle(targetID, attackerID):
            return
        super(EpicBattleMessagesPlayer, self).showVehicleKilledMessage(avatar, targetID, attackerID, equipmentID, reason)

    def _messageIsAllowedInEpicBattle(self, targetID, attackerID):
        componentSystem = self._arenaVisitor.getComponentSystem()
        if componentSystem is not None:
            playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
            if playerDataComp is not None:
                voTarget = self._arenaDP.getVehicleStats(targetID)
                voAttacker = self._arenaDP.getVehicleStats(attackerID)
                targetLane = voTarget.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PLAYER_GROUP)
                attackerLane = voAttacker.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PLAYER_GROUP)
                playerLane = playerDataComp.physicalLane
                if playerLane != targetLane and playerLane != attackerLane:
                    return False
        return True


class EpicBattleMessagesController(BattleMessagesController):

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        if not self._messageIsAllowedInEpicBattle(targetID, attackerID):
            return
        super(EpicBattleMessagesController, self).showVehicleKilledMessage(avatar, targetID, attackerID, equipmentID, reason)

    def _messageIsAllowedInEpicBattle(self, targetID, attackerID):
        componentSystem = self._arenaVisitor.getComponentSystem()
        if componentSystem is not None:
            playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
            if playerDataComp is not None:
                voTarget = self._arenaDP.getVehicleStats(targetID)
                voAttacker = self._arenaDP.getVehicleStats(attackerID)
                targetLane = voTarget.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PLAYER_GROUP)
                attackerLane = voAttacker.gameModeSpecific.getValue(EPIC_BATTLE_KEYS.PLAYER_GROUP)
                playerLane = playerDataComp.physicalLane
                if playerLane != targetLane and playerLane != attackerLane:
                    return False
        return True


@dependency.replace_none_kwargs(battleSessionProvider=IBattleSessionProvider)
def _isVehicleSpawnedBot(vehicleID, battleSessionProvider=None):
    ctx = battleSessionProvider.getCtx()
    vTypeInfoVO = ctx.getArenaDP().getVehicleInfo(vehicleID).vehicleType
    return isSpawnedBot(vTypeInfoVO.tags)


@dependency.replace_none_kwargs(battleSessionProvider=IBattleSessionProvider)
def _getSpawnedBotMsgData(vehicleID, battleSessionProvider=None):
    ctx = battleSessionProvider.getCtx()
    vTypeInfoVO = ctx.getArenaDP().getVehicleInfo(vehicleID).vehicleType
    if isSpawnedBot(vTypeInfoVO.tags):
        botMasterPlayer = ctx.getPlayerFullName(vehicleID, showVehShortName=False)
        playerInfo = '%s (%s)' % (botMasterPlayer, vTypeInfoVO.shortNameWithPrefix)
        return ('ALLY_HIT', {'entity': playerInfo}, (('entity', vehicleID),))
    else:
        return None


class BattleRoyaleBattleMessagesController(BattleMessagesController):

    def showAllyHitMessage(self, vehicleID=None):
        spawnBotData = _getSpawnedBotMsgData(vehicleID)
        if spawnBotData:
            self.onShowPlayerMessageByKey(*spawnBotData)
            return
        super(BattleRoyaleBattleMessagesController, self).showAllyHitMessage(vehicleID)

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        if _isVehicleSpawnedBot(targetID):
            return
        super(BattleRoyaleBattleMessagesController, self).showVehicleKilledMessage(avatar, targetID, attackerID, equipmentID, reason)


class BattleRoyaleBattleMessagesPlayer(BattleMessagesPlayer):

    def showAllyHitMessage(self, vehicleID=None):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        spawnBotData = _getSpawnedBotMsgData(vehicleID)
        if spawnBotData:
            self.onShowPlayerMessageByKey(*spawnBotData)
            return
        super(BattleRoyaleBattleMessagesPlayer, self).showAllyHitMessage(vehicleID)

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        if _isVehicleSpawnedBot(targetID):
            return
        super(BattleRoyaleBattleMessagesPlayer, self).showVehicleKilledMessage(avatar, targetID, attackerID, equipmentID, reason)


class R4Messages(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _playVehicleKilledNotification(self, avatar, targetID, attackerID):
        soundNotify = avatar.soundNotifications
        vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
        target = vehicles[targetID]
        if not (target.isObserver or target.isCommander) and not target.isSupply and target.isAlly:
            aliveVehiclesCount = len(vehicles.values(lambda v: not (v.isObserver or v.isCommander) and not v.isSupply and v.isAlly and v.isAlive))
            if aliveVehiclesCount > len(R4_SOUND.R4_ALLY_DESTROYED_EVENTS) - 1:
                soundNotify.playOnHeadVehicle(R4_SOUND.R4_ALLY_DESTROYED)
            else:
                soundNotify.playOnHeadVehicle(R4_SOUND.R4_ALLY_DESTROYED_EVENTS[aliveVehiclesCount])
            soundNotify.play(R4_SOUND.R4_ALLY_DESTROYED_UI, targetID)
            return
        attacker = vehicles[attackerID]
        if not (not (target.isObserver or target.isCommander) and not target.isSupply and not target.isAlly and not (attacker.isObserver or attacker.isCommander) and attacker.isAlly):
            return
        enemies = vehicles.values(lambda v: not (v.isObserver or v.isCommander) and not v.isSupply and not v.isAlly)
        enemiesCount = len(enemies)
        aliveEnemiesCount = len([ e for e in enemies if e.isAlive ])
        destroyedEnemiesCount = enemiesCount - aliveEnemiesCount
        halfEnemiesCount = math.ceil(enemiesCount / 2.0) if random.randrange(2) else math.floor(enemiesCount / 2.0)
        canPlayCounter = destroyedEnemiesCount < len(R4_SOUND.R4_ENEMY_DESTROYED_COUNTER_EVENTS)
        canPlayRemain = aliveEnemiesCount < len(R4_SOUND.R4_ENEMY_DESTROYED_REMAIN_EVENTS)
        if canPlayCounter and canPlayRemain:
            if aliveEnemiesCount > halfEnemiesCount:
                soundNotify.play(R4_SOUND.R4_ENEMY_DESTROYED_COUNTER_EVENTS[destroyedEnemiesCount], attackerID)
            else:
                soundNotify.play(R4_SOUND.R4_ENEMY_DESTROYED_REMAIN_EVENTS[aliveEnemiesCount], attackerID)
        elif canPlayCounter:
            soundNotify.play(R4_SOUND.R4_ENEMY_DESTROYED_COUNTER_EVENTS[destroyedEnemiesCount], attackerID)
        elif canPlayRemain:
            soundNotify.play(R4_SOUND.R4_ENEMY_DESTROYED_REMAIN_EVENTS[aliveEnemiesCount], attackerID)
        else:
            soundNotify.play(R4_SOUND.R4_ENEMY_DESTROYED, attackerID)


class R4MessagesPlayer(BattleMessagesPlayer, R4Messages):

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        BattleMessagesPlayer.showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason)
        R4Messages._playVehicleKilledNotification(self, avatar, targetID, attackerID)


class R4MessagesController(BattleMessagesController, R4Messages):

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        BattleMessagesController.showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason)
        R4Messages._playVehicleKilledNotification(self, avatar, targetID, attackerID)


def createBattleMessagesCtrl(setup):
    sessionProvider = dependency.instance(IBattleSessionProvider)
    arenaVisitor = sessionProvider.arenaVisitor
    gui = arenaVisitor.gui
    if gui.isInEpicRange():
        if setup.isReplayPlaying:
            ctrl = EpicBattleMessagesPlayer(setup)
        else:
            ctrl = EpicBattleMessagesController(setup)
    elif gui.isBattleRoyale():
        if setup.isReplayPlaying:
            ctrl = BattleRoyaleBattleMessagesPlayer(setup)
        else:
            ctrl = BattleRoyaleBattleMessagesController(setup)
    elif avatar_getter.isPlayerCommander():
        if setup.isReplayPlaying:
            ctrl = R4MessagesPlayer(setup)
        else:
            ctrl = R4MessagesController(setup)
    elif setup.isReplayPlaying:
        ctrl = BattleMessagesPlayer(setup)
    else:
        ctrl = BattleMessagesController(setup)
    return ctrl
