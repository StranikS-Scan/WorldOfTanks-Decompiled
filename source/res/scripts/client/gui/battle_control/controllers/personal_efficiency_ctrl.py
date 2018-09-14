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
        """
        Constructor.
        :param etype: Efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        """
        super(_EfficiencyInfo, self).__init__()
        self.__type = etype

    def getType(self):
        """
        Returns efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        """
        return self.__type


class _FeedbackEventEfficiencyInfo(_EfficiencyInfo):
    __slots__ = ('__battleEventType', '__arenaVehID')

    def __init__(self, etype, event):
        """
        Constructor
        
        :param etype: Efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        :param event: any _FeedbackEvent derived event
        """
        super(_FeedbackEventEfficiencyInfo, self).__init__(etype)
        self.__battleEventType = event.getBattleEventType()
        self.__arenaVehID = event.getTargetID()

    def getBattleEventType(self):
        """
        Returns type of battle event. For details see BATTLE_EVENT_TYPE.
        """
        return self.__battleEventType

    def getArenaVehicleID(self):
        return self.__arenaVehID


class _DamageEfficiencyInfo(_FeedbackEventEfficiencyInfo):
    __slots__ = ('__damage',)

    def __init__(self, etype, event):
        """
        Constructor
        
        :param etype: Efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        :param event: any _FeedbackEvent derived event
        """
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

    def isShellGold(self):
        return self.__damage.isShellGold()

    def getShellType(self):
        """
        Returns shell type (see SHELL_TYPES enum) or None, if shell type is not defined.
        """
        return self.__damage.getShellType()


class _CriticalHitsEfficiencyInfo(_FeedbackEventEfficiencyInfo):
    __slots__ = ('__critsExtra',)

    def __init__(self, etype, event):
        """
        Constructor
        
        :param etype: Efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        :param event: any _FeedbackEvent derived event
        """
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

    def isShellGold(self):
        return self.__critsExtra.isShellGold()

    def getShellType(self):
        """
        Returns shell type (see SHELL_TYPES enum) or None, if shell type is not defined.
        """
        return self.__critsExtra.getShellType()


_AGGREGATED_DAMAGE_EFFICIENCY_TYPES = (_ETYPE.DAMAGE, _ETYPE.ASSIST_DAMAGE, _ETYPE.BLOCKED_DAMAGE)
_FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE = {_FET.PLAYER_DAMAGED_HP_ENEMY: (_ETYPE.DAMAGE, _DamageEfficiencyInfo),
 _FET.PLAYER_ASSIST_TO_KILL_ENEMY: (_ETYPE.ASSIST_DAMAGE, _DamageEfficiencyInfo),
 _FET.PLAYER_USED_ARMOR: (_ETYPE.BLOCKED_DAMAGE, _DamageEfficiencyInfo),
 _FET.ENEMY_DAMAGED_HP_PLAYER: (_ETYPE.RECEIVED_DAMAGE, _DamageEfficiencyInfo),
 _FET.ENEMY_DAMAGED_DEVICE_PLAYER: (_ETYPE.RECEIVED_CRITICAL_HITS, _CriticalHitsEfficiencyInfo)}

def _createEfficiencyInfoFromFeedbackEvent(event):
    """
    Factory method to create efficiency data (info) from a feedback event
    
    :param event: any _FeedbackEvent derived event
    :return: _EfficiencyInfo child based on the feedback type or None.
    """
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

    def getTotalEfficiency(self, type):
        """
        Returns total efficiency by the given type.
        :param type: efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        """
        return self.__totalEfficiency[type]

    def getLoogedEfficiency(self, types):
        """
        Returns logged efficiency by the given type mask.
        :param types: damage types represented by bit mask (see PERSONAL_EFFICIENCY_TYPE)
        :return: list of _DamageInfo objects
        """
        return [ d for d in reversed(self.__efficiencyLog) if BitmaskHelper.hasAnyBitSet(types, d.getType()) ]

    def _onPlayerFeedbackReceived(self, events):
        """
        Handler of player's feedback events (see FEEDBACK_EVENT_ID).
        :param events: List of PlayerFeedbackEvent objects
        """
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
        """
        Handler of FEEDBACK_EVENT_ID.DAMAGE_LOG_SUMMARY feedback event.
        :param event: An instance of BattleSummaryFeedbackEvent
        """
        self.__totalEfficiency[_ETYPE.DAMAGE] = event.getTotalDamage()
        self.__totalEfficiency[_ETYPE.BLOCKED_DAMAGE] = event.getTotalBlockedDamage()
        self.__totalEfficiency[_ETYPE.ASSIST_DAMAGE] = event.getTotalAssistDamage()
        self.onTotalEfficiencyUpdated(dict(self.__totalEfficiency))

    def _onVehicleChanged(self, *args, **kwargs):
        if self.__arenaDP.isPlayerObserver():
            self.__efficiencyLog.clear()
            self.onPersonalEfficiencyLogSynced()


def createEfficiencyCtrl(setup, feedback, vehStateCtrl):
    return PersonalEfficiencyController(setup.arenaDP, feedback, vehStateCtrl)
