# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/personal_efficiency_ctrl.py
import weakref
from collections import defaultdict, deque
import Event
from shared_utils import BitmaskHelper
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE as _ETYPE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
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

    def isFire(self):
        return self.__damage.isFire()

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
 _ETYPE.STUN)
_FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE = {_FET.PLAYER_DAMAGED_HP_ENEMY: (_ETYPE.DAMAGE, _DamageEfficiencyInfo),
 _FET.PLAYER_ASSIST_TO_KILL_ENEMY: (_ETYPE.ASSIST_DAMAGE, _DamageEfficiencyInfo),
 _FET.PLAYER_USED_ARMOR: (_ETYPE.BLOCKED_DAMAGE, _DamageEfficiencyInfo),
 _FET.ENEMY_DAMAGED_HP_PLAYER: (_ETYPE.RECEIVED_DAMAGE, _DamageEfficiencyInfo),
 _FET.ENEMY_DAMAGED_DEVICE_PLAYER: (_ETYPE.RECEIVED_CRITICAL_HITS, _CriticalHitsEfficiencyInfo),
 _FET.DESTRUCTIBLE_DAMAGED: (_ETYPE.DAMAGE, _DestructibleDamagedEfficiencyInfo),
 _FET.PLAYER_ASSIST_TO_STUN_ENEMY: (_ETYPE.STUN, _DamageEfficiencyInfo)}

def _createEfficiencyInfoFromFeedbackEvent(event):
    if event.getType() in _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE:
        etype, cls = _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE[event.getType()]
        return cls(etype, event)
    else:
        return None


class PersonalEfficiencyController(IBattleController):

    def __init__(self, arenaDP, feedback, vehStateCtrl):
        super(PersonalEfficiencyController, self).__init__()
        self.__arenaDP = weakref.proxy(arenaDP)
        self.__feedback = weakref.proxy(feedback)
        self.__vehStateCtrl = weakref.proxy(vehStateCtrl)
        self.__eManager = Event.EventManager()
        self.onTotalEfficiencyUpdated = Event.Event(self.__eManager)
        self.onPersonalEfficiencyReceived = Event.Event(self.__eManager)
        self.onPersonalEfficiencyLogSynced = Event.Event(self.__eManager)
        self.__totalEfficiency = defaultdict(int)
        self.__efficiencyLog = deque(maxlen=_LOG_MAX_LEN)

    def getControllerID(self):
        return BATTLE_CTRL_ID.PERSONAL_EFFICIENCY

    def startControl(self):
        self.__feedback.onPlayerFeedbackReceived += self._onPlayerFeedbackReceived
        self.__feedback.onPlayerSummaryFeedbackReceived += self._onPlayerSummaryFeedbackReceived
        self.__vehStateCtrl.onVehicleControlling += self._onVehicleChanged

    def stopControl(self):
        self.__arenaDP = None
        self.__feedback = None
        self.__vehStateCtrl = None
        self.__eManager.clear()
        self.__eManager = None
        return

    def getTotalEfficiency(self, eType):
        return self.__totalEfficiency[eType]

    def getLoogedEfficiency(self, types):
        return [ d for d in reversed(self.__efficiencyLog) if BitmaskHelper.hasAnyBitSet(types, d.getType()) ]

    def _onPlayerFeedbackReceived(self, events):
        eventsCount = 0
        totals = defaultdict(int)
        for event in events:
            info = _createEfficiencyInfoFromFeedbackEvent(event)
            if info is not None:
                eventsCount += 1
                if info.getType() in _AGGREGATED_DAMAGE_EFFICIENCY_TYPES:
                    totals[info.getType()] = totals[info.getType()] + info.getDamage()
                self.__efficiencyLog.appendleft(info)

        if eventsCount > 0:
            eventsCount = min(eventsCount, _LOG_MAX_LEN)
            if totals:
                for key in totals.iterkeys():
                    self.__totalEfficiency[key] = self.__totalEfficiency[key] + totals[key]
                    totals[key] = self.__totalEfficiency[key]

                self.onTotalEfficiencyUpdated(totals)
            self.onPersonalEfficiencyReceived([ self.__efficiencyLog[i] for i in range(eventsCount - 1, -1, -1) ])
        return

    def _onPlayerSummaryFeedbackReceived(self, event):
        self.__totalEfficiency[_ETYPE.DAMAGE] = event.getTotalDamage()
        self.__totalEfficiency[_ETYPE.BLOCKED_DAMAGE] = event.getTotalBlockedDamage()
        self.__totalEfficiency[_ETYPE.ASSIST_DAMAGE] = event.getTotalAssistDamage()
        self.__totalEfficiency[_ETYPE.STUN] = event.getTotalStunDamage()
        self.onTotalEfficiencyUpdated(dict(self.__totalEfficiency))

    def _onVehicleChanged(self, *args, **kwargs):
        if self.__arenaDP.isPlayerObserver():
            self.__efficiencyLog.clear()
            self.onPersonalEfficiencyLogSynced()


def createEfficiencyCtrl(setup, feedback, vehStateCtrl):
    return PersonalEfficiencyController(setup.arenaDP, feedback, vehStateCtrl)
