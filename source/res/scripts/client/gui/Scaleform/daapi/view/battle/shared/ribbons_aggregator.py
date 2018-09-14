# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ribbons_aggregator.py
import Event
from debug_utils import LOG_UNEXPECTED
from collections import defaultdict, OrderedDict
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as _BET
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID

class _Ribbon(object):
    __slots__ = ()

    def __init__(self, event):
        """
        Constructor. Creates a new ribbon from the given event feedback.
        
        :param event: _FeedbackEvent derived instance
        """
        super(_Ribbon, self).__init__()

    def getType(self):
        """
        Returns efficiency type (see BATTLE_EFFICIENCY_TYPES)
        """
        raise NotImplementedError

    def canAggregate(self, ribbon):
        """
        Returns True if ribbon can aggregated data from the given one. False - otherwise.
        :param ribbon: An instance of _Ribbon derived class
        """
        return self.getType() == ribbon.getType()

    def aggregate(self, ribbon):
        assert self.getType() == ribbon.getType()


class _BasePointsRibbon(_Ribbon):
    __slots__ = ('_points',)

    def __init__(self, event):
        super(_BasePointsRibbon, self).__init__(event)
        self._points = event.getExtra()

    def getType(self):
        raise NotImplementedError

    def getPoints(self):
        """
        Returns base points represented by int.
        """
        return self._points

    def canAggregate(self, ribbon):
        return False


class _BaseCaptureRibbon(_BasePointsRibbon):
    __slots__ = ('_sessionID',)

    def __init__(self, event):
        super(_BaseCaptureRibbon, self).__init__(event)
        self._sessionID = event.getTargetID()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.CAPTURE

    def getSessionID(self):
        return self._sessionID

    def canAggregate(self, ribbon):
        return self.getType() == ribbon.getType() and self._sessionID == ribbon.getSessionID()

    def aggregate(self, ribbon):
        super(_BaseCaptureRibbon, self).aggregate(ribbon)
        self._points += ribbon.getPoints()


class _BaseDefenceRibbon(_BasePointsRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DEFENCE


class _VehicleCounterRibbon(_Ribbon):
    __slots__ = ('_vehIDs',)

    def __init__(self, event):
        super(_VehicleCounterRibbon, self).__init__(event)
        self._vehIDs = [event.getTargetID()]

    def getType(self):
        raise NotImplementedError

    def getVehIDs(self):
        return self._vehIDs[:]

    def getCount(self):
        return len(self._vehIDs)

    def aggregate(self, ribbon):
        super(_VehicleCounterRibbon, self).aggregate(ribbon)
        self._vehIDs.extend(ribbon.getVehIDs())


class _EnemyKillRibbon(_VehicleCounterRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DESTRUCTION


class _EnemyDetectionRibbon(_VehicleCounterRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DETECTION


class _SingleVehicleDamageRibbon(_Ribbon):
    __slots__ = ('_damage', '_targetVehID')

    def __init__(self, event):
        super(_SingleVehicleDamageRibbon, self).__init__(event)
        self._damage = event.getExtra().getDamage()
        self._targetVehID = event.getTargetID()

    def getType(self):
        raise NotImplementedError

    def getDamage(self):
        return self._damage

    def getVehicleID(self):
        return self._targetVehID

    def canAggregate(self, ribbon):
        return super(_SingleVehicleDamageRibbon, self).canAggregate(ribbon) and self._targetVehID == ribbon.getVehicleID()

    def aggregate(self, ribbon):
        super(_SingleVehicleDamageRibbon, self).aggregate(ribbon)
        self._damage += ribbon.getDamage()


class _CausedDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE


class _BlockedDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ARMOR


class _MultiVehicleHitRibbon(_Ribbon):
    __slots__ = ('_hits',)

    def __init__(self, event):
        super(_MultiVehicleHitRibbon, self).__init__(event)
        self._hits = defaultdict(int)
        self._hits[event.getTargetID()] = self._parseExtra(event)

    def getType(self):
        raise NotImplementedError

    def getVehIDs(self):
        return self._hits.keys()

    def getExtraSum(self):
        return sum(self._hits.itervalues())

    def aggregate(self, ribbon):
        super(_MultiVehicleHitRibbon, self).aggregate(ribbon)
        for targetID, extra in ribbon._hits.iteritems():
            self._hits[targetID] += extra

    @classmethod
    def _parseExtra(cls, event):
        return event.getExtra()


class _CriticalHitRibbon(_MultiVehicleHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.CRITS


class _MultiVehicleDamageRibbon(_MultiVehicleHitRibbon):
    __slots__ = ()

    def getType(self):
        raise NotImplementedError

    @classmethod
    def _parseExtra(cls, event):
        return event.getExtra().getDamage()


class _TrackAssistRibbon(_MultiVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ASSIST_TRACK


class _RadioAssistRibbon(_MultiVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ASSIST_SPOT


class _FireHitRibbon(_MultiVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.BURN


class _RamHitRibbon(_MultiVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RAM


_FEEDBACK_EVENT_TO_RIBBON_CLS = {FEEDBACK_EVENT_ID.PLAYER_CAPTURED_BASE: _BaseCaptureRibbon,
 FEEDBACK_EVENT_ID.PLAYER_DROPPED_CAPTURE: _BaseDefenceRibbon,
 FEEDBACK_EVENT_ID.PLAYER_SPOTTED_ENEMY: _EnemyDetectionRibbon,
 FEEDBACK_EVENT_ID.PLAYER_USED_ARMOR: _BlockedDamageRibbon,
 FEEDBACK_EVENT_ID.PLAYER_DAMAGED_DEVICE_ENEMY: _CriticalHitRibbon,
 FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY: _EnemyKillRibbon}

class ATTACK_REASON(object):
    SHOT = 'shot'
    FIRE = 'fire'
    RAM = 'ramming'
    WORLD_COLLISION = 'world_collision'
    DEATH_ZONE = 'death_zone'
    DROWNING = 'drowning'
    GAS_ATTACK = 'gas_attack'
    OVERTURN = 'overturn'


def _createRibbonFromPlayerFeedbackEvent(event):
    ribbonCls = None
    etype = event.getType()
    if etype in _FEEDBACK_EVENT_TO_RIBBON_CLS:
        ribbonCls = _FEEDBACK_EVENT_TO_RIBBON_CLS[etype]
    elif etype == FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY:
        if event.getBattleEventType() == _BET.TRACK_ASSIST:
            ribbonCls = _TrackAssistRibbon
        elif event.getBattleEventType() == _BET.RADIO_ASSIST:
            ribbonCls = _RadioAssistRibbon
    elif etype == FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY:
        damageExtra = event.getExtra()
        if damageExtra.isShot():
            ribbonCls = _CausedDamageRibbon
        elif damageExtra.isFire():
            ribbonCls = _FireHitRibbon
        else:
            ribbonCls = _RamHitRibbon
    if ribbonCls is not None:
        return ribbonCls(event)
    else:
        LOG_UNEXPECTED('Could not find a proper ribbon class associated with the given feedback event', event)
        return


class _Rule(object):
    __slots__ = ('__type',)

    def __init__(self, ribbon):
        super(_Rule, self).__init__()
        self.__type = ribbon.getType()

    def getType(self):
        return self.__type

    def isValid(self, ribbon):
        """
        Checks whether the given ribbon corresponds to the rule.
        
        :param ribbon: An instance of _Ribbon class
        :return: True if rule is satisfied, False - otherwise.
        """
        raise NotImplementedError

    def update(self, rule):
        """
        Update rule by the given rule.
        
        :param rule: An instance of _Rule class
        :return: True if rule has been updated.
        """
        return False


class _IgnoreRuleByKill(_Rule):
    __slots__ = ('_vehIDs',)

    def __init__(self, ribbon):
        super(_IgnoreRuleByKill, self).__init__(ribbon)
        self._vehIDs = set()
        self.update(ribbon)

    def isValid(self, ribbon):
        """
        Checks the following rule: ignore damage-related ribbons after kill ribbon for the targets
        stored in rule.
        
        :param ribbon: An instance of _Ribbon class
        :return: True if rule is satisfied, False - otherwise.
        """
        etype = ribbon.getType()
        if etype == BATTLE_EFFICIENCY_TYPES.DAMAGE:
            return ribbon.getVehicleID() not in self._vehIDs
        return not self._vehIDs.issuperset(set(ribbon.getVehIDs())) if etype in (BATTLE_EFFICIENCY_TYPES.BURN, BATTLE_EFFICIENCY_TYPES.RAM) else True

    def update(self, rule):
        if rule.getType() == self.getType():
            self._vehIDs.update(rule._vehIDs)
            return True
        return False


class RibbonsAggregator(object):

    def __init__(self):
        super(RibbonsAggregator, self).__init__()
        self.__feedbackProvider = None
        self.__cache = {}
        self.__rules = {}
        self.onRibbonAdded = Event.Event()
        self.onRibbonUpdated = Event.Event()
        return

    def start(self):
        if self.__feedbackProvider is None:
            self.__feedbackProvider = g_sessionProvider.shared.feedback
            self.__feedbackProvider.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        return

    def stop(self):
        self.clearRibbonsData()
        self.clearRules()
        self.onRibbonAdded.clear()
        self.onRibbonUpdated.clear()
        if self.__feedbackProvider is not None:
            self.__feedbackProvider.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
            self.__feedbackProvider = None
        return

    def clearRibbonData(self, etype):
        """
        Clears ribbon of the given type from the inner cache.
        :param etype: ribbon type (see BATTLE_EFFICIENCY_TYPES)
        """
        self.__cache.pop(etype, None)
        return

    def clearRibbonsData(self):
        """
        Clears all cached ribbons.
        """
        self.__cache.clear()

    def clearRules(self):
        """
        Clears all rules.
        """
        self.__rules.clear()

    def _checkRules(self, ribbon):
        for rule in self.__rules.itervalues():
            if not rule.isValid(ribbon):
                return False

        return True

    def _updateRules(self, ribbons):
        for ribbon in ribbons:
            etype = ribbon.getType()
            if etype == BATTLE_EFFICIENCY_TYPES.DESTRUCTION:
                newRule = _IgnoreRuleByKill(ribbon)
                if etype in self.__rules:
                    rule = self.__rules[etype]
                    rule.update(newRule)
                else:
                    self.__rules[etype] = newRule

    def __onPlayerFeedbackReceived(self, events):
        """
        Callback on player feedback event (see BattleFeedbackAdaptor). Aggregates player feedback
        events according to some rules and converts them to appropriate battle efficiency events
        (see _FEEDBACK_EVENT_TO_RIBBON_CLS). Puts ribbons to the inner cache and triggers
        appropriate RibbonsAggregator events.
        
        There are 3 aggregation rules of ribbons:
        1. Ribbons are not aggregated (base capture and base defence)
        2. Ribbons are aggregated by vehicle ID (all damage types and blocked damage)
        3. All other ribbons are aggregated.
        Note that knowledge about aggregation is kept in each ribbon type/class (see canAggregate
        method).
        
        :param events: list of PlayerFeedbackEvent
        """
        ribbons = OrderedDict()
        for event in events:
            ribbon = _createRibbonFromPlayerFeedbackEvent(event)
            if ribbon is not None and self._checkRules(ribbon):
                if ribbon.getType() in ribbons:
                    temporaryRibbons = ribbons.pop(ribbon.getType())
                    if len(temporaryRibbons) > 1:
                        for index, temporaryRibbon in enumerate(temporaryRibbons):
                            if temporaryRibbon.canAggregate(ribbon):
                                item = temporaryRibbons.pop(index)
                                item.aggregate(ribbon)
                                temporaryRibbons.append(item)
                                break
                        else:
                            temporaryRibbons.append(ribbon)

                    else:
                        tmpRibbon = temporaryRibbons[0]
                        if tmpRibbon.canAggregate(ribbon):
                            tmpRibbon.aggregate(ribbon)
                        else:
                            temporaryRibbons.append(ribbon)
                    ribbons[ribbon.getType()] = temporaryRibbons
                else:
                    ribbons[ribbon.getType()] = [ribbon]

        sortedRibbons = self.__getSortedList(ribbons)
        for ribbon in sortedRibbons:
            etype = ribbon.getType()
            if etype in self.__cache:
                cachedRibbon = self.__cache[etype]
                if cachedRibbon.canAggregate(ribbon):
                    cachedRibbon.aggregate(ribbon)
                    ribbon = cachedRibbon
                else:
                    self.__cache[etype] = ribbon
                self.onRibbonUpdated(ribbon)
            self.__cache[etype] = ribbon
            self.onRibbonAdded(ribbon)

        self._updateRules(sortedRibbons)
        return

    @staticmethod
    def __getSortedList(ribbons):
        """
        Sort events according to the following rules:
        1. Enemy kill ribbon should appear at the end of the list.
        2. Enemy detection ribbon should appear at the top of the list.
        
        NOTE: according to aggregation rules, the output ribbons don't contain duplicates of
        ribbons with the same type). If there are a few ribbons with the same type in the
        server response, use the last one.
        
        :param ribbons: OrderedDict of ribbons to be resorted according to rules described above
                        and converted to the list without duplicates.
        
        :return: Sorted ribbons list.
        """
        sortedRibons = []
        if ribbons:
            killRibbons = ribbons.pop(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, None)
            detectionRibbons = ribbons.pop(BATTLE_EFFICIENCY_TYPES.DETECTION, None)
            if detectionRibbons is not None:
                sortedRibons.append(detectionRibbons[-1])
            for newRibbons in ribbons.itervalues():
                sortedRibons.append(newRibbons[-1])

            if killRibbons is not None:
                sortedRibons.append(killRibbons[-1])
        return sortedRibons
