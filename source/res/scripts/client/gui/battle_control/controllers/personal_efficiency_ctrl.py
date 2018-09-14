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
_DAMAGE_EFFICIENCY_INFO = (_ETYPE.DAMAGE, _ETYPE.ASSIST_DAMAGE, _ETYPE.BLOCKED_DAMAGE)
_FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE = {_FET.PLAYER_DAMAGED_HP_ENEMY: _ETYPE.DAMAGE,
 _FET.PLAYER_ASSIST_TO_KILL_ENEMY: _ETYPE.ASSIST_DAMAGE,
 _FET.PLAYER_USED_ARMOR: _ETYPE.BLOCKED_DAMAGE}

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

    @classmethod
    def fromFeedbackEvent(cls, etype, event):
        """
        Creates efficiency info object from the given _FeedbackEvent derived event.
        
        :param etype: Efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        :param event: any _FeedbackEvent derived event
        :return: _EfficiencyInfo child
        """
        return _EfficiencyInfo(etype)


class _DamageEfficiencyInfo(_EfficiencyInfo):
    __slots__ = ('__damage', '__battleEventType', '__arenaVehID')

    def __init__(self, etype, battleEventType, arenaVehID, damage):
        """
        Constructor
        
        :param etype: Efficiency type (see PERSONAL_EFFICIENCY_TYPE)
        :param damage: An instance of _DamageExtra (see feedback_events.py)
        :param battleEventType: Battle event type (see BATTLE_EVENT_TYPE)
        :param arenaVehID: Attacker/Target arena vehicle ID
        """
        super(_DamageEfficiencyInfo, self).__init__(etype)
        self.__damage = damage
        self.__battleEventType = battleEventType
        self.__arenaVehID = arenaVehID

    def getDamage(self):
        return self.__damage.getDamage()

    def getBattleEventType(self):
        """
        Returns type of battle event. For details see BATTLE_EVENT_TYPE.
        """
        return self.__battleEventType

    def getArenaVehicleID(self):
        return self.__arenaVehID

    def isFire(self):
        return self.__damage.isFire()

    def isRam(self):
        return self.__damage.isRam()

    def isShot(self):
        return self.__damage.isShot()

    @classmethod
    def fromFeedbackEvent(self, etype, event):
        return _DamageEfficiencyInfo(etype, event.getBattleEventType(), event.getTargetID(), event.getExtra())


_PERSONAL_EFFICIENCY_TYPE_TO_INFO_CLS = {_ETYPE.DAMAGE: _DamageEfficiencyInfo,
 _ETYPE.ASSIST_DAMAGE: _DamageEfficiencyInfo,
 _ETYPE.BLOCKED_DAMAGE: _DamageEfficiencyInfo}

def _createEfficiencyInfoFromFeedbackEvent(event):
    """
    Factory method to create efficiency data (info) from a feedback event
    
    :param event: any _FeedbackEvent derived event
    :return: _EfficiencyInfo child based on the feedback type or None.
    """
    if event.getType() in _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE:
        etype = _FEEDBACK_EVENT_TYPE_TO_PERSONAL_EFFICIENCY_TYPE[event.getType()]
        cls = _PERSONAL_EFFICIENCY_TYPE_TO_INFO_CLS[etype]
        return cls.fromFeedbackEvent(etype, event)
    else:
        return None


class PersonalEfficiencyController(IBattleController):

    def __init__(self, feedback):
        super(PersonalEfficiencyController, self).__init__()
        self.__feedback = weakref.proxy(feedback)
        self.__eManager = Event.EventManager()
        self.onTotalEfficiencyUpdated = Event.Event(self.__eManager)
        self.onPersonalEfficiencyReceived = Event.Event(self.__eManager)
        self.__totalEfficiency = defaultdict(int)
        self.__efficiencyLog = deque(maxlen=_LOG_MAX_LEN)

    def getControllerID(self):
        return BATTLE_CTRL_ID.PERSONAL_EFFICIENCY

    def startControl(self):
        self.__feedback.onPlayerFeedbackReceived += self._onPlayerFeedbackReceived
        self.__feedback.onPlayerSummaryFeedbackReceived += self._onPlayerSummaryFeedbackReceived

    def stopControl(self):
        self.__feedback = None
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
        damageEventsCount = 0
        damageTotals = defaultdict(int)
        for event in events:
            info = _createEfficiencyInfoFromFeedbackEvent(event)
            if info is not None and info.getType() in _DAMAGE_EFFICIENCY_INFO:
                damageEventsCount += 1
                damageTotals[info.getType()] = damageTotals[info.getType()] + info.getDamage()
                self.__efficiencyLog.appendleft(info)

        if damageEventsCount > 0:
            damageEventsCount = min(damageEventsCount, _LOG_MAX_LEN)
            for key in damageTotals.iterkeys():
                self.__totalEfficiency[key] = self.__totalEfficiency[key] + damageTotals[key]
                damageTotals[key] = self.__totalEfficiency[key]

            self.onTotalEfficiencyUpdated(damageTotals)
            self.onPersonalEfficiencyReceived([ self.__efficiencyLog[i] for i in range(damageEventsCount - 1, -1, -1) ])
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


class PersonalEfficiencyPlayer(PersonalEfficiencyController):

    def _onPlayerFeedbackReceived(self, events):
        pass

    def _onPlayerSummaryFeedbackReceived(self, event):
        pass


def createEfficiencyCtrl(setup, feedback):
    if setup.isReplayPlaying:
        ctrl = PersonalEfficiencyPlayer(feedback)
    else:
        ctrl = PersonalEfficiencyController(feedback)
    return ctrl
