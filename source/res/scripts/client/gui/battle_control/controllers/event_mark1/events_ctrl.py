# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_mark1/events_ctrl.py
import weakref
from collections import deque
from CTFManager import g_ctfManager
from gui.shared.lock import Lock
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, BATTLE_SYNC_LOCKS
from gui.battle_control.controllers.event_mark1.common import SoundViewComponentsController
from constants import FLAG_TYPES, FLAG_STATE, MARK1_TEAM_NUMBER
_NOTIFICATION_QUEUE_MAX_LEN = 3

class STATES(object):
    NEW_BONUS_REPAIR_KIT_ATTACK = 'newBonusRepairAttack'
    NEW_BONUS_BOMB_DEFENCE = 'newBonusBombDefence'
    MARK1_STOPPED_BY_DESTRUCTION_ATTACK = 'markStoppedByDestructionAttack'
    MARK1_STOPPED_BY_DESTRUCTION_DEFENCE = 'markStoppedByDestructionDefence'
    BOMB_CAPTURED_ATTACK = 'bombForMarkCaptured'
    MARK1_REPAIRED_ATTACK = 'mark1RepairedAttack'
    MARK1_REPAIRED_DEFENCE = 'mark1RepairedDefence'
    REPAIR_KIT_CAPTURED_DEFENCE = 'repairKitCaptured'


_SOUND_MAP = {STATES.MARK1_STOPPED_BY_DESTRUCTION_ATTACK: 'mark1_stopped_attack',
 STATES.MARK1_STOPPED_BY_DESTRUCTION_DEFENCE: 'mark1_stopped_defence',
 STATES.MARK1_REPAIRED_ATTACK: 'mark1_repaired_attack',
 STATES.MARK1_REPAIRED_DEFENCE: 'mark1_repaired_defence'}

class Mark1EventNotificationController(SoundViewComponentsController):
    __onSpawn = {FLAG_TYPES.EXPLOSIVE: ({'state': STATES.NEW_BONUS_BOMB_DEFENCE,
                             'markTeam': False},),
     FLAG_TYPES.REPAIR_KIT: ({'state': STATES.NEW_BONUS_REPAIR_KIT_ATTACK,
                              'markTeam': True},)}
    __onCaptured = {FLAG_TYPES.EXPLOSIVE: ({'state': STATES.BOMB_CAPTURED_ATTACK,
                             'markTeam': True},),
     FLAG_TYPES.REPAIR_KIT: ({'state': STATES.REPAIR_KIT_CAPTURED_DEFENCE,
                              'markTeam': False},)}
    __onAbsorbed = {FLAG_TYPES.REPAIR_KIT: ({'state': STATES.MARK1_REPAIRED_ATTACK,
                              'markTeam': True}, {'state': STATES.MARK1_REPAIRED_DEFENCE,
                              'markTeam': False})}
    __onBonusCtrlBombExploded = ({'state': STATES.MARK1_STOPPED_BY_DESTRUCTION_ATTACK,
      'markTeam': True}, {'state': STATES.MARK1_STOPPED_BY_DESTRUCTION_DEFENCE,
      'markTeam': False})

    def __init__(self, setup, bonusCtrl):
        super(Mark1EventNotificationController, self).__init__()
        self.__ui = None
        self.__callbackID = None
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__bonusCtrl = bonusCtrl
        self.__notificationQueue = deque(maxlen=_NOTIFICATION_QUEUE_MAX_LEN)
        self.__viewLock = Lock(BATTLE_SYNC_LOCKS.MARK1_EVENT_NOTIFICATIONS)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.MARK1_EVENT_NOTS

    def startControl(self, *args):
        self.__viewLock.onUnlocked += self.__onViewLockUnlocked
        self.__showEventsOnStart()
        g_ctfManager.onFlagSpawnedAtBase += self.__onFlagSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        if self.__bonusCtrl is not None:
            self.__bonusCtrl.onBombExploded += self.__onBombExploded
            self.__bonusCtrl.onLastBombPlanted += self.__onLastBombPlanted
        if self.__ui is not None:
            self.__ui.onStateHidden += self.__onNotificationHidden
        return

    def stopControl(self):
        g_ctfManager.onFlagSpawnedAtBase -= self.__onFlagSpawnedAtBase
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        if self.__bonusCtrl is not None:
            self.__bonusCtrl.onBombExploded -= self.__onBombExploded
            self.__bonusCtrl.onLastBombPlanted -= self.__onLastBombPlanted
        if self.__ui is not None:
            self.__ui.onStateHidden -= self.__onNotificationHidden
        self.__notificationQueue.clear()
        self.__viewLock.dispose()
        self.clearViewComponents()
        self.__callbackID = None
        self.__arenaDP = None
        return

    def setViewComponents(self, *components):
        self.__ui = components[0]
        self.__ui.onStateHidden += self.__onNotificationHidden
        self.__showEventsOnStart()

    def clearViewComponents(self):
        self.__ui = None
        return

    def _getSoundMap(self):
        return _SOUND_MAP

    def __onFlagSpawnedAtBase(self, flagID, flagTeam, flagPos):
        self.__update(flagID, self.__onSpawn)

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        self.__update(flagID, self.__onCaptured)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        self.__update(flagID, self.__onAbsorbed)

    def __onBombExploded(self):
        if self.__ui is not None:
            self.__updateByConditions(self.__onBonusCtrlBombExploded)
        return

    def __onLastBombPlanted(self):
        self.clearViewComponents()

    def __showEventsOnStart(self):
        for flagID, flagInfo in g_ctfManager.getFlags():
            state = flagInfo['state']
            flagTeam = flagInfo['team']
            if state == FLAG_STATE.ON_SPAWN:
                self.__onFlagSpawnedAtBase(flagID, flagTeam, None)
            if state == FLAG_STATE.ON_VEHICLE:
                self.__onFlagCapturedByVehicle(flagID, flagTeam, None)
            if state == FLAG_STATE.ABSORBED:
                self.__onFlagAbsorbed(flagID, flagTeam, None, None)

        return

    def __update(self, flagID, mapping):
        if self.__ui is not None:
            flagType = g_ctfManager.getFlagType(flagID)
            if flagType in mapping:
                stateConditions = mapping[flagType]
                self.__updateByConditions(stateConditions)
        return

    def __updateByConditions(self, stateConditions):
        for condition in stateConditions:
            isMarkTeam = self.__arenaDP.getNumberOfTeam() == MARK1_TEAM_NUMBER
            if isMarkTeam == condition['markTeam']:
                self.__addToQueue(condition['state'])

    def __showNotification(self, state):
        if self.__ui is not None:
            self.__ui.showState(state)
            self._playSound(state)
        return

    def __onNotificationHidden(self, state):
        self.__checkQueue()

    def __onViewLockUnlocked(self):
        self.__checkQueue()

    def __addToQueue(self, state):
        self.__notificationQueue.append(state)
        self.__checkQueue()

    def __checkQueue(self):
        if self.__notificationQueue:
            if self.__viewLock.tryLock():
                self.__showNotification(self.__notificationQueue.pop())
        else:
            self.__viewLock.unlock()
