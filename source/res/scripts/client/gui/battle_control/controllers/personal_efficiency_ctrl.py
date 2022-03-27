# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/personal_efficiency_ctrl.py
import weakref
from collections import defaultdict, deque
import Event
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import dependency
from shared_utils import BitmaskHelper
from skeletons.gui.battle_session import IBattleSessionProvider
_LOG_MAX_LEN = 100

class _EfficiencyInfo(object):
    __slots__ = ('__type',)

    def __init__(self, etype):
        super(_EfficiencyInfo, self).__init__()
        self.__type = etype

    def getType(self):
        return self.__type


class _FeedbackEventEfficiencyInfo(_EfficiencyInfo):
    __slots__ = ('__battleEventType', '__arenaVehID')

    def __init__(self, etype, event):
        super(_FeedbackEventEfficiencyInfo, self).__init__(etype)
        self.__battleEventType = event.getBattleEventType()
        self.__arenaVehID = event.getTargetID()

    def getBattleEventType(self):
        return self.__battleEventType

    def getArenaVehicleID(self):
        return self.__arenaVehID


class _DamageEfficiencyInfo(_FeedbackEventEfficiencyInfo):
    __slots__ = ('__damage',)

    def __init__(self, etype, event):
        super(_DamageEfficiencyInfo, self).__init__(etype, event)
        self.__damage = event.getExtra()

    def getDamage(self):
        return self.__damage.getDamage()

    def isSpawnedBotExplosion(self, primary=True):
        return self.__damage.isSpawnedBotExplosion(primary=primary)

    def isSpawnedBotRam(self, primary=True):
        return self.__damage.isSpawnedBotRam(primary=primary)

    def isHidden(self):
        return self.__damage.isNone()

    def isFire(self):
        return self.__damage.isFire()

    def isBerserker(self):
        return self.__damage.isBerserker()

    def isMinefield(self):
        return self.__damage.isMinefield()

    def isDamagingSmoke(self):
        return self.__damage.isDamagingSmoke()

    def isRam(self):
        return self.__damage.isRam()

    def isShot(self):
        return self.__damage.isShot()

    def isWorldCollision(self):
        return self.__damage.isWorldCollision()

    def isDeathZone(self):
        return self.__damage.isDeathZone()

    def isShellGold(self):
        return self.__damage.isShellGold()

    def isProtectionZoneDamage(self, primary=True):
        return self.__damage.isProtectionZone(primary=primary)

    def isArtilleryEqDamage(self, primary=True):
        return self.__damage.isArtilleryEq(primary=primary)

    def isBomberEqDamage(self, primary=True):
        return self.__damage.isBomberEq(primary=primary)

    def isBombersDamage(self, primary=True):
        return self.__damage.isBombers(primary=primary)

    def isMineFieldDamage(self, primary=True):
        return self.__damage.isMineField(primary=primary)

    def getShellType(self):
        return self.__damage.getShellType()


class _CriticalHitsEfficiencyInfo(_FeedbackEventEfficiencyInfo):
    __slots__ = ('__critsExtra',)

    def __init__(self, etype, event):
        super(_CriticalHitsEfficiencyInfo, self).__init__(etype, event)
        self.__critsExtra = event.getExtra()

    def getCritsCount(self):
        return self.__critsExtra.getCritsCount()

    def isFire(self):
        return self.__critsExtra.isFire()

    def isBerserker(self):
        return self.__critsExtra.isBerserker()

    def isMinefield(self):
        return self.__critsExtra.isMinefield()

    def isDamagingSmoke(self):
        return self.__critsExtra.isDamagingSmoke()

    def isRam(self):
        return self.__critsExtra.isRam()

    def isShot(self):
        return self.__critsExtra.isShot()

    def isWorldCollision(self):
        return self.__critsExtra.isWorldCollision()

    def isDeathZone(self):
        return self.__critsExtra.isDeathZone()

    def isShellGold(self):
        return self.__critsExtra.isShellGold()

    def isProtectionZoneDamage(self, primary=True):
        return self.__critsExtra.isProtectionZone(primary=primary)

    def isArtilleryEqDamage(self, primary=True):
        return self.__critsExtra.isArtilleryEq(primary=primary)

    def isBomberEqDamage(self, primary=True):
        return self.__critsExtra.isBomberEq(primary=primary)

    def isBombersDamage(self, primary=True):
        return self.__critsExtra.isBombers(primary=primary)

    def getShellType(self):
        return self.__critsExtra.getShellType()


class _DestructibleDamagedEfficiencyInfo(_FeedbackEventEfficiencyInfo):
    __slots__ = ('__damage',)

    def __init__(self, etype, event):
        super(_DestructibleDamagedEfficiencyInfo, self).__init__(etype, event)
        self.__damage = event.getExtra()

    def getDamage(self):
        return self.__damage

    def isProtectionZoneDamage(self):
        return False

    def isArtilleryEqDamage(self, primary=True):
        return False

    def isBomberEqDamage(self, primary=True):
        return False

    def isBombersDamage(self):
        return False

    def isShot(self):
        return True

    def isDeathZone(self):
        return False


_AGGREGATED_DAMAGE_EFFICIENCY_TYPES = (_ETYPE.DAMAGE,
 _ETYPE.ASSIST_DAMAGE,
 _ETYPE.BLOCKED_DAMAGE,
 _ETYPE.STUN,
 _ETYPE.SUPPLY_DAMAGE)
_FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE = {_FET.PLAYER_DAMAGED_HP_ENEMY: (_ETYPE.DAMAGE, _DamageEfficiencyInfo),
 _FET.PLAYER_ASSIST_TO_KILL_ENEMY: (_ETYPE.ASSIST_DAMAGE, _DamageEfficiencyInfo),
 _FET.PLAYER_USED_ARMOR: (_ETYPE.BLOCKED_DAMAGE, _DamageEfficiencyInfo),
 _FET.ENEMY_DAMAGED_HP_PLAYER: (_ETYPE.RECEIVED_DAMAGE, _DamageEfficiencyInfo),
 _FET.ENEMY_DAMAGED_DEVICE_PLAYER: (_ETYPE.RECEIVED_CRITICAL_HITS, _CriticalHitsEfficiencyInfo),
 _FET.DESTRUCTIBLE_DAMAGED: (_ETYPE.DAMAGE, _DestructibleDamagedEfficiencyInfo),
 _FET.PLAYER_ASSIST_TO_STUN_ENEMY: (_ETYPE.STUN, _DamageEfficiencyInfo),
 _FET.PLAYER_DAMAGED_SUPPLY_ENEMY: (_ETYPE.SUPPLY_DAMAGE, _DamageEfficiencyInfo)}

def _createEfficiencyInfoFromFeedbackEvent(event):
    if event.getType() in _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE:
        etype, cls = _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE[event.getType()]
        return cls(etype, event)
    else:
        return None


def _totalEfficiencyToDict(totalEfficiency):
    return {vehID:dict(data) for vehID, data in totalEfficiency.iteritems()}


class PersonalEfficiencyController(IBattleController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, arenaDP, feedback, vehStateCtrl):
        super(PersonalEfficiencyController, self).__init__()
        self.__arenaDP = weakref.proxy(arenaDP)
        self.__feedback = weakref.proxy(feedback)
        self._vehStateCtrl = weakref.proxy(vehStateCtrl)
        self.__eManager = Event.EventManager()
        self.onTotalEfficiencyUpdated = Event.Event(self.__eManager)
        self.onPersonalEfficiencyReceived = Event.Event(self.__eManager)
        self.onPersonalEfficiencyLogSynced = Event.Event(self.__eManager)
        self.onTotalEfficiencyInvalid = Event.Event(self.__eManager)
        self._totalEfficiency = defaultdict(lambda : defaultdict(int))
        self._efficiencyLog = defaultdict(lambda : deque(maxlen=_LOG_MAX_LEN))

    def getControllerID(self):
        return BATTLE_CTRL_ID.PERSONAL_EFFICIENCY

    def startControl(self):
        self.__feedback.onPlayerFeedbackReceived += self._onPlayerFeedbackReceived
        self.__feedback.onPlayerSummaryFeedbackReceived += self._onPlayerSummaryFeedbackReceived
        self._vehStateCtrl.onVehicleControlling += self._onVehicleChanged

    def stopControl(self):
        self.__arenaDP = None
        self.__feedback = None
        self._vehStateCtrl = None
        self.__eManager.clear()
        self.__eManager = None
        return

    def getTotalEfficiency(self, eType, vehicleID=0):
        if not vehicleID:
            vehicleID = self._vehStateCtrl.getControllingVehicleID()
        return self._totalEfficiency[vehicleID][eType]

    def getLoogedEfficiency(self, types):
        return [ d for d in reversed(self._efficiencyLog[self._vehStateCtrl.getControllingVehicleID()]) if BitmaskHelper.hasAnyBitSet(types, d.getType()) ]

    def _onPlayerFeedbackReceived(self, vehicleID, events):
        eventsCount = 0
        totals = defaultdict(int)
        for event in events:
            info = _createEfficiencyInfoFromFeedbackEvent(event)
            if info is not None:
                eventsCount += 1
                if info.getType() in _AGGREGATED_DAMAGE_EFFICIENCY_TYPES:
                    totals[info.getType()] = totals[info.getType()] + info.getDamage()
                self._efficiencyLog[vehicleID].appendleft(info)

        if eventsCount > 0:
            eventsCount = min(eventsCount, _LOG_MAX_LEN)
            if totals:
                for key in totals.iterkeys():
                    self._totalEfficiency[vehicleID][key] = self._totalEfficiency[vehicleID][key] + totals[key]
                    totals[key] = self._totalEfficiency[vehicleID][key]

                self.onTotalEfficiencyUpdated({vehicleID: dict(totals)})
            self.onPersonalEfficiencyReceived([ self._efficiencyLog[vehicleID][i] for i in range(eventsCount - 1, -1, -1) ])
        return

    def _onPlayerSummaryFeedbackReceived(self, vehicleID, event):
        self._totalEfficiency[vehicleID][_ETYPE.DAMAGE] = event.getTotalDamage()
        self._totalEfficiency[vehicleID][_ETYPE.BLOCKED_DAMAGE] = event.getTotalBlockedDamage()
        self._totalEfficiency[vehicleID][_ETYPE.ASSIST_DAMAGE] = event.getTotalAssistDamage()
        self._totalEfficiency[vehicleID][_ETYPE.STUN] = event.getTotalStunDamage()
        self._totalEfficiency[vehicleID][_ETYPE.SUPPLY_DAMAGE] = event.getTotalDamageSupply()
        self.onTotalEfficiencyUpdated(_totalEfficiencyToDict(self._totalEfficiency))

    def _onVehicleChanged(self, *args, **kwargs):
        if self.__arenaDP.isPlayerObserver():
            self._efficiencyLog.clear()
            self.onPersonalEfficiencyLogSynced()


class PersonalEfficiencyControllerCommander(PersonalEfficiencyController):

    def _onPlayerFeedbackReceived(self, vehicleID, events):
        commanderVehID = avatar_getter.commanderVehicleID()
        currentVehicleID = self._vehStateCtrl.getControllingVehicleID()
        if vehicleID == commanderVehID:
            return
        else:
            eventsCount = 0
            totalUpdate = False
            for event in events:
                info = _createEfficiencyInfoFromFeedbackEvent(event)
                if info is not None:
                    eventsCount += 1
                    eventType = info.getType()
                    if eventType in _AGGREGATED_DAMAGE_EFFICIENCY_TYPES:
                        self._totalEfficiency[vehicleID][eventType] += info.getDamage()
                        self._totalEfficiency[commanderVehID][eventType] += info.getDamage()
                        totalUpdate = True
                    self._efficiencyLog[vehicleID].appendleft(info)

            if totalUpdate:
                self.onTotalEfficiencyUpdated(_totalEfficiencyToDict(self._totalEfficiency))
            if eventsCount > 0 and vehicleID == currentVehicleID:
                eventsCount = min(eventsCount, _LOG_MAX_LEN)
                self.onPersonalEfficiencyReceived([ self._efficiencyLog[vehicleID][i] for i in range(eventsCount - 1, -1, -1) ])
            return

    def _onPlayerSummaryFeedbackReceived(self, vehicleID, event):
        commanderVehID = avatar_getter.commanderVehicleID()
        if vehicleID == commanderVehID:
            return
        eventTypesToTrack = {_ETYPE.DAMAGE: event.getTotalDamage(),
         _ETYPE.SUPPLY_DAMAGE: event.getTotalDamageSupply(),
         _ETYPE.BLOCKED_DAMAGE: event.getTotalBlockedDamage(),
         _ETYPE.ASSIST_DAMAGE: event.getTotalAssistDamage(),
         _ETYPE.STUN: event.getTotalStunDamage()}
        for eventType, value in eventTypesToTrack.iteritems():
            self._totalEfficiency[vehicleID][eventType] = value

        commanderEfficiency = self._totalEfficiency.setdefault(commanderVehID, defaultdict(int))
        for eventType in eventTypesToTrack.iterkeys():
            commanderEfficiency[eventType] = 0

        for vehID, vehTotalEfficiency in self._totalEfficiency.iteritems():
            if vehID == commanderVehID:
                continue
            for eventType, value in vehTotalEfficiency.iteritems():
                commanderEfficiency[eventType] += value

        self.onTotalEfficiencyUpdated(_totalEfficiencyToDict(self._totalEfficiency))

    def _onVehicleChanged(self, *args, **kwargs):
        self._efficiencyLog.clear()
        self.onPersonalEfficiencyLogSynced()
        self.onTotalEfficiencyInvalid()
        self.onTotalEfficiencyUpdated(_totalEfficiencyToDict(self._totalEfficiency))


def createEfficiencyCtrl(setup, feedback, vehStateCtrl):
    return PersonalEfficiencyControllerCommander(setup.arenaDP, feedback, vehStateCtrl) if avatar_getter.isPlayerCommander() else PersonalEfficiencyController(setup.arenaDP, feedback, vehStateCtrl)
