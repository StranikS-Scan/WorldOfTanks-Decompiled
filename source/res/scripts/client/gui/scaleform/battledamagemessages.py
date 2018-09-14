# Embedded file name: scripts/client/gui/Scaleform/BattleDamageMessages.py
import BigWorld
import Event
from gui.battle_control import g_sessionProvider

class BattleDamageMessages(object):

    class ATTACK_REASON:
        ATTACK = 0
        FIRE = 1
        RAMMING = 2
        WORLD_COLLISION = 3
        DEATH_ZONE = 4
        DROWNING = 5

    class ENTITY_TYPE:
        UNKNOWN = 'unknown'
        SELF = 'self'
        ALLY = 'ally'
        ENEMY = 'enemy'
        SUICIDE = 'suicide'

    ATTACK_REASON_CODE = {ATTACK_REASON.ATTACK: 'DEATH_FROM_SHOT',
     ATTACK_REASON.FIRE: 'DEATH_FROM_SHOT',
     ATTACK_REASON.RAMMING: 'DEATH_FROM_RAMMING',
     ATTACK_REASON.WORLD_COLLISION: 'DEATH_FROM_WORLD_COLLISION',
     ATTACK_REASON.DEATH_ZONE: 'DEATH_FROM_DEATH_ZONE',
     ATTACK_REASON.DROWNING: 'DEATH_FROM_DROWNING'}
    PLAYER_KILL_ENEMY_SOUND = 'enemy_killed_by_player'
    PLAYER_KILL_ALLY_SOUND = 'ally_killed_by_player'

    def __init__(self):
        self.onShowVehicleMessage = Event.Event()
        self.onShowPlayerMessage = Event.Event()

    def destroy(self):
        self.onShowVehicleMessage.clear()
        self.onShowPlayerMessage.clear()

    def onArenaVehicleKilled(self, targetID, attackerID, reason):
        if not hasattr(BigWorld.player(), 'playerVehicleID'):
            return
        else:
            p = BigWorld.player()
            isMyVehicle = targetID == BigWorld.player().playerVehicleID
            isObservedVehicle = not p.isVehicleAlive and targetID == p.inputHandler.ctrl.curVehicleID
            if isMyVehicle or isObservedVehicle:
                return
            if targetID == attackerID and g_sessionProvider.getCtx().isObserver(targetID):
                return
            code, postfix, sound = self.__getKillInfo(targetID, attackerID, reason)
            if sound is not None:
                p.soundNotifications.play(sound)
            self.onShowPlayerMessage(code, postfix, targetID, attackerID)
            return

    def showVehicleDamageInfo(self, code, entityID, extra):
        p = BigWorld.player()
        if not hasattr(p, 'playerVehicleID'):
            return
        targetID = p.playerVehicleID
        if not p.isVehicleAlive and entityID == p.inputHandler.ctrl.curVehicleID:
            targetID = entityID
        code, postfix = self.__getDamageInfo(code, entityID, targetID)
        self.onShowPlayerMessage(code, postfix, targetID, entityID)
        self.onShowVehicleMessage(code, postfix, entityID, extra)

    def __getEntityString(self, entityID):
        p = BigWorld.player()
        if entityID == p.playerVehicleID:
            return self.ENTITY_TYPE.SELF
        else:
            entityInfo = p.arena.vehicles.get(entityID)
            if entityInfo is not None:
                if entityInfo['team'] != p.team:
                    return self.ENTITY_TYPE.ENEMY
                else:
                    return self.ENTITY_TYPE.ALLY
            return self.ENTITY_TYPE.UNKNOWN

    def __getDamageInfo(self, code, entityID, targetID):
        postfix = ''
        target = self.__getEntityString(targetID)
        if not entityID or entityID == targetID:
            postfix = '%s_%s' % (target.upper(), self.ENTITY_TYPE.SUICIDE.upper())
        else:
            entity = self.__getEntityString(entityID)
            postfix = '%s_%s' % (entity.upper(), target.upper())
        return (code, postfix)

    def __getKillInfo(self, targetID, attackerID, reason):
        attacker = self.__getEntityString(attackerID)
        target = self.ENTITY_TYPE.SUICIDE
        if targetID != attackerID:
            target = self.__getEntityString(targetID)
        code = self.ATTACK_REASON_CODE.get(reason)
        sound = None
        if attackerID == BigWorld.player().playerVehicleID:
            if target == self.ENTITY_TYPE.ENEMY:
                sound = self.PLAYER_KILL_ENEMY_SOUND
            elif target == self.ENTITY_TYPE.ALLY:
                sound = self.PLAYER_KILL_ALLY_SOUND
        return (code, '%s_%s' % (attacker.upper(), target.upper()), sound)
