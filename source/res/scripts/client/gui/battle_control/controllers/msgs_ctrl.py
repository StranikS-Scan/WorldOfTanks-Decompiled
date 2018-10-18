# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/msgs_ctrl.py
import weakref
import BattleReplay
import BigWorld
import Event
import event_points_event_type as _eventType
from ReplayEvents import g_replayEvents
from constants import ATTACK_REASON_INDICES as _AR_INDICES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.arena_info.arena_vos import EPIC_BATTLE_KEYS

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
 _AR_INDICES['bomber_eq']: 'DEATH_FROM_SHOT'}
_EVENT_TYPES = {_eventType.PLAYER_DIED: ('halloweenSin', '<font color="#000000">{}</font>', '<img src="img://gui/maps/icons/pveEvent/logIconSoul.png" vspace="-4"/>'),
 _eventType.POINTS_SAVED: ('halloweenSalvation', '{}', '<img src="img://gui/maps/icons/pveEvent/logIconSoulSaved.png" vspace="-3"/>'),
 _eventType.POINTS_PICKED: ('halloweenBliss', '<font color="#000000">{}</font>', '<img src="img://gui/maps/icons/pveEvent/logIconSoul.png" vspace="-4"/>')}
_PLAYER_KILL_ENEMY_SOUND = 'enemy_killed_by_player'
_PLAYER_KILL_ALLY_SOUND = 'ally_killed_by_player'
_ALLY_KILLED_SOUND = 'ally_killed_by_enemy'
_NAME_TRUNCATE_LENGTH = 16

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
        elif targetID == attackerID and self._battleCtx.isObserver(targetID):
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

    def showAllyHitMessage(self, vehicleID=None):
        self.onShowPlayerMessageByKey('ALLY_HIT', {'entity': self._battleCtx.getPlayerFullName(vID=vehicleID)}, (('entity', vehicleID),))

    def showEventPointsMessage(self, event):
        pass

    def __getEntityString(self, avatar, entityID):
        if entityID == avatar.playerVehicleID:
            return _ENTITY_TYPE.SELF
        if self._battleCtx.isAlly(entityID):
            return _ENTITY_TYPE.ALLY
        return _ENTITY_TYPE.ENEMY if self._battleCtx.isEnemy(entityID) else _ENTITY_TYPE.UNKNOWN

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
        soundExt = None
        if attackerID == BigWorld.player().playerVehicleID:
            if target == _ENTITY_TYPE.ENEMY:
                sound = _PLAYER_KILL_ENEMY_SOUND
            elif target == _ENTITY_TYPE.ALLY:
                sound = _PLAYER_KILL_ALLY_SOUND
                soundExt = _ALLY_KILLED_SOUND
        elif target == _ENTITY_TYPE.ALLY or target == _ENTITY_TYPE.SUICIDE and attacker == _ENTITY_TYPE.ALLY:
            soundExt = _ALLY_KILLED_SOUND
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


class EventBattleMessagesController(BattleMessagesController):
    __slots__ = ('_isReplayPlaying',)

    def __init__(self, setup):
        super(EventBattleMessagesController, self).__init__(setup)
        self._isReplayPlaying = setup.isReplayPlaying

    def showDestructibleEntityDestroyedMessage(self, avatar, destructibleID, attackerID):
        pass

    def showVehicleKilledMessage(self, avatar, targetID, attackerID, equipmentID, reason):
        pass

    def showVehicleDamageInfo(self, avatar, code, targetID, entityID, extra, equipmentID):
        pass

    def showVehicleMessage(self, key, args=None):
        pass

    def showVehicleError(self, key, args=None):
        pass

    def showAllyHitMessage(self, vehicleID=None):
        pass

    def showEventPointsMessage(self, event):
        if self._isReplayPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            eventTypeData = _EVENT_TYPES.get(event.type)
            if eventTypeData:
                typeName, colorFormat, icon = eventTypeData
                formatName = self._battleCtx.getPlayerFullName
                truncateName = lambda name, width: name[:width] + '..' if len(name) > width else name
                pointsStr = str(event.points)
                alignFormat = '{{:^{}}}'.format(6 - len(pointsStr))
                pointsStr = alignFormat.format(pointsStr)
                pointsStr = colorFormat.format(pointsStr)
                pointsStr = '{}{}'.format(pointsStr, icon)
                args = {'player': truncateName(formatName(event.vehicleID, showVehShortName=False, showClan=False), _NAME_TRUNCATE_LENGTH),
                 'enemy': formatName(event.enemyID, showClan=False) if event.enemyID else None,
                 'points': pointsStr}
                self.onShowPlayerMessageByKey(typeName, args)
            return


def createBattleMessagesCtrl(setup):
    sessionProvider = dependency.instance(IBattleSessionProvider)
    arenaVisitor = sessionProvider.arenaVisitor
    if arenaVisitor.gui.isInEpicRange():
        if setup.isReplayPlaying:
            ctrl = EpicBattleMessagesPlayer(setup)
        else:
            ctrl = EpicBattleMessagesController(setup)
    elif arenaVisitor.gui.isEventBattle():
        ctrl = EventBattleMessagesController(setup)
    elif setup.isReplayPlaying:
        ctrl = BattleMessagesPlayer(setup)
    else:
        ctrl = BattleMessagesController(setup)
    return ctrl
