# Embedded file name: scripts/client/gui/battle_control/battle_msgs_ctrl.py
import BattleReplay
import BigWorld
import Event
from constants import ATTACK_REASON_INDICES as _AR_INDICES
from gui.battle_control.arena_info import isEventBattle

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
 _AR_INDICES['drowning']: 'DEATH_FROM_DROWNING'}
_PLAYER_KILL_ENEMY_SOUND = 'enemy_killed_by_player'
_PLAYER_KILL_ALLY_SOUND = 'ally_killed_by_player'

class BattleMessagesController(object):
    __slots__ = ('__battleCtx', '__eManager', '_buffer', '_isUIPopulated', 'onShowVehicleMessageByCode', 'onShowVehicleMessageByKey', 'onShowVehicleErrorByKey', 'onShowPlayerMessageByCode', 'onShowPlayerMessageByKey')

    def __init__(self):
        self.__battleCtx = None
        self.__eManager = Event.EventManager()
        self.onShowVehicleMessageByCode = Event.Event(self.__eManager)
        self.onShowVehicleMessageByKey = Event.Event(self.__eManager)
        self.onShowVehicleErrorByKey = Event.Event(self.__eManager)
        self.onShowPlayerMessageByCode = Event.Event(self.__eManager)
        self.onShowPlayerMessageByKey = Event.Event(self.__eManager)
        self._buffer = []
        self._isUIPopulated = False
        return

    def start(self, battleCtx):
        self.__battleCtx = battleCtx

    def stop(self):
        self.__eManager.clear()
        self.__battleCtx = None
        return

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        try:
            playerVehicleID = avatar.playerVehicleID
        except AttributeError:
            return

        isMyVehicle = targetID == playerVehicleID
        isObservedVehicle = not avatar.isVehicleAlive and targetID == avatar.inputHandler.ctrl.curVehicleID
        if isMyVehicle or isObservedVehicle:
            return
        elif targetID == attackerID and self.__battleCtx.isObserver(targetID):
            return
        else:
            code, postfix, sound = self.__getKillInfo(avatar, targetID, attackerID, equipmentID, reason)
            if sound is not None:
                avatar.soundNotifications.play(sound)
            self.onShowPlayerMessageByCode(code, postfix, targetID, attackerID, equipmentID)
            return

    def showVehicleDamageInfo(self, avatar, code, entityID, extra, equipmentID):
        try:
            targetID = avatar.playerVehicleID
        except AttributeError:
            return

        if not avatar.isVehicleAlive and entityID == avatar.inputHandler.ctrl.curVehicleID:
            targetID = entityID
        code, postfix = self.__getDamageInfo(avatar, code, entityID, targetID)
        self.onShowPlayerMessageByCode(code, postfix, targetID, entityID, equipmentID)
        self.onShowVehicleMessageByCode(code, postfix, entityID, extra, equipmentID)

    def showVehicleMessage(self, key, args = None):
        self.onShowVehicleMessageByKey(key, args, None)
        return

    def showVehicleError(self, key, args = None):
        self.onShowVehicleErrorByKey(key, args, None)
        return

    def showAllyHitMessage(self, vehicleID = None):
        self.onShowPlayerMessageByKey('ALLY_HIT', {'entity': self.__battleCtx.getFullPlayerName(vID=vehicleID)}, (('entity', vehicleID),))

    def __getEntityString(self, avatar, entityID):
        if entityID == avatar.playerVehicleID:
            return _ENTITY_TYPE.SELF
        elif self.__battleCtx.isAlly(entityID):
            return _ENTITY_TYPE.ALLY
        elif self.__battleCtx.isEnemy(entityID):
            return _ENTITY_TYPE.ENEMY
        else:
            return _ENTITY_TYPE.UNKNOWN

    def __getDamageInfo(self, avatar, code, entityID, targetID):
        target = self.__getEntityString(avatar, targetID)
        if not entityID or entityID == targetID:
            postfix = '%s_%s' % (target.upper(), _ENTITY_TYPE.SUICIDE.upper())
        else:
            entity = self.__getEntityString(avatar, entityID)
            postfix = '%s_%s' % (entity.upper(), target.upper())
        return (code, postfix)

    def __getKillInfo(self, avatar, targetID, attackerID, equipmentID, reason):
        attacker = self.__getEntityString(avatar, attackerID)
        target = _ENTITY_TYPE.SUICIDE
        if targetID != attackerID:
            target = self.__getEntityString(avatar, targetID)
        code = _ATTACK_REASON_CODE.get(reason)
        sound = None
        if attackerID == BigWorld.player().playerVehicleID:
            if target == _ENTITY_TYPE.ENEMY:
                sound = _PLAYER_KILL_ENEMY_SOUND
            elif target == _ENTITY_TYPE.ALLY:
                sound = _PLAYER_KILL_ALLY_SOUND
        return (code, '%s_%s' % (attacker.upper(), target.upper()), sound)

    def onUIPopulated(self):
        self._isUIPopulated = True
        for args in self._buffer:
            self.onShowVehicleMessageByKey(*args)


class BattleMessagesPlayer(BattleMessagesController):

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleKilledMessage(avatar, targetID, attackerID, equipmentID, reason)

    def showVehicleDamageInfo(self, avatar, code, entityID, extra, equipmentID):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleDamageInfo(avatar, code, entityID, extra, equipmentID)

    def showVehicleMessage(self, key, args = None):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleMessage(key, args)

    def showVehicleError(self, key, args = None):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showVehicleError(key, args)

    def showAllyHitMessage(self, vehicleID = None):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        super(BattleMessagesPlayer, self).showAllyHitMessage(vehicleID)

    def showInfoMessage(self, key, withBuffer = False, args = None):
        if withBuffer and not self._isUIPopulated:
            self._buffer.append((key, args))
        else:
            super(BattleMessagesPlayer, self).showVehicleMessage(key, args)


def createBattleMessagesCtrl(isReplayPlaying):
    if isReplayPlaying:
        ctrl = BattleMessagesPlayer()
    else:
        ctrl = BattleMessagesController()
    return ctrl
