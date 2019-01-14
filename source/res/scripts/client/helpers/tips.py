# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/tips.py
import logging
import re
import sys
from collections import defaultdict, namedtuple
import constants
import nations
from constants import ARENA_GUI_TYPE
from gui.impl.gen import R
from gui.shared.utils.functions import rnd_choice_loop
from helpers import dependency
from items.vehicles import VEHICLE_CLASS_TAGS
from skeletons.gui.battle_session import IBattleSessionProvider
ALL = 'all'
ANY = 'any'
EXCEPT = 'except'
INFINITY_STR_VALUE = 'infinity'
TIPS_ADD_PATTERN_PARTS_COUNT = 7
EPIC_TIPS_ADD_PATTERN_PARTS_COUNT = 2
BATTLE_CONDITIONS_PARTS_COUNT = 3
_FoundTip = namedtuple('_FoundTip', 'status, body, icon')
_logger = logging.getLogger(__name__)

class _TipsCriteria(object):
    __slots__ = ('_count', '_classTag', '_nation', '_level')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(_TipsCriteria, self).__init__()
        self._count = 0
        self._classTag = ALL
        self._nation = ALL
        self._level = 1

    def getBattleCount(self):
        return self._count

    def setBattleCount(self, count):
        self._count = count
        return self

    def getClassTag(self):
        return self._classTag

    def setClassTag(self, tag):
        self._classTag = tag
        return self

    def getNation(self):
        return self._nation

    def setNation(self, nation):
        self._nation = nation
        return self

    def getLevel(self):
        return self._level

    def setLevel(self, level):
        self._level = level
        return self

    def find(self):
        raise NotImplementedError


class RandomTipsCriteria(_TipsCriteria):

    def find(self):
        iterator = getTipsIterator(constants.ARENA_GUI_TYPE.RANDOM, self._count, self._classTag, self._nation, self._level)
        if iterator is not None:
            tip = _FoundTip(*next(iterator))
        else:
            tip = _FoundTip(R.invalid(), R.invalid(), '')
        return tip


class EpicBattleTipsCriteria(RandomTipsCriteria):

    def find(self):
        iterator = self.__getTipsIterator(self._count)
        if iterator is not None:
            tip = _FoundTip(*next(iterator))
        else:
            tip = _FoundTip(R.invalid(), R.invalid(), '')
        return tip

    def __getTipsIterator(self, battlesCount):
        tipsItems = _getEpicBattleConditionedTips(battlesCount)
        return rnd_choice_loop(*tipsItems) if tipsItems > 0 else None


_SANDBOX_GEOMETRY_INDEX = ('100_thepit', '10_hills')

class SandboxTipsCriteria(_TipsCriteria):

    def find(self):
        playerBaseYPos = enemyBaseYPos = 0
        arenaDP = self.sessionProvider.getCtx().getArenaDP()
        playerTeam = 1
        if arenaDP is not None:
            playerTeam = arenaDP.getNumberOfTeam()
        visitor = self.sessionProvider.arenaVisitor
        positions = visitor.type.getTeamBasePositionsIterator()
        for team, position, _ in positions:
            if team == playerTeam:
                playerBaseYPos = position[2]
            enemyBaseYPos = position[2]

        geometryName = visitor.type.getGeometryName()
        if geometryName in _SANDBOX_GEOMETRY_INDEX:
            geometryIndex = _SANDBOX_GEOMETRY_INDEX.index(geometryName)
        else:
            geometryIndex = 0
        positionIndex = 0 if playerBaseYPos < enemyBaseYPos else 1
        iconKey = 'sandbox{0}{1}'.format(str(geometryIndex), str(positionIndex))
        return _FoundTip(R.strings.tips.howToPlay(), R.strings.tips.dyn('sandbox{}'.format(geometryIndex))(), R.images.gui.maps.icons.battleLoading.tips.dyn(iconKey)())


class EventTipsCriteria(_TipsCriteria):

    def find(self):
        return _FoundTip(R.strings.tips.eventTitle(), R.strings.tips.eventMessage(), R.images.gui.maps.icons.battleLoading.tips.event())


def _getRankedTipIterator():
    tipSize = R.strings.tips.ranked.length()
    if tipSize > 0:
        items = range(tipSize)
        return rnd_choice_loop(*items)
    else:
        return None


class RankedTipsCriteria(_TipsCriteria):
    __tipIterator = None

    def __init__(self):
        super(RankedTipsCriteria, self).__init__()
        if RankedTipsCriteria.__tipIterator is None:
            RankedTipsCriteria.__tipIterator = _getRankedTipIterator()
        return

    def find(self):
        iterator = RankedTipsCriteria.__tipIterator
        if iterator is not None:
            tipNum = next(iterator)
            rankedTipRes = R.strings.tips.ranked.dyn('c_{}'.format(tipNum))
            if rankedTipRes:
                return _FoundTip(rankedTipRes.title(), rankedTipRes.body(), R.images.gui.maps.icons.battleLoading.tips.dyn('ranked{}'.format(tipNum))())
        return _FoundTip(R.invalid(), R.invalid(), '')


def _getEpicRandomTipIterator():
    tipSize = R.strings.tips.epicRandom.length()
    if tipSize > 0:
        items = range(tipSize)
        return rnd_choice_loop(*items)
    else:
        return None


class EpicRandomTipsCriteria(_TipsCriteria):
    __tipIterator = None

    def __init__(self):
        super(EpicRandomTipsCriteria, self).__init__()
        if EpicRandomTipsCriteria.__tipIterator is None:
            EpicRandomTipsCriteria.__tipIterator = _getEpicRandomTipIterator()
        return

    def find(self):
        iterator = EpicRandomTipsCriteria.__tipIterator
        if iterator is not None:
            tipNum = next(iterator)
            epicTipRes = R.strings.tips.epicRandom.dyn('c_{}'.format(tipNum))
            if epicTipRes:
                return _FoundTip(epicTipRes.title(), epicTipRes.body(), R.images.gui.maps.icons.battleLoading.tips.dyn('epicRandom{}'.format(tipNum))())
        return _FoundTip('', '', '')


def getTipsCriteria(arenaVisitor):
    if arenaVisitor.gui.isSandboxBattle():
        return SandboxTipsCriteria()
    if arenaVisitor.gui.isEventBattle():
        return EventTipsCriteria()
    if arenaVisitor.gui.isRankedBattle():
        return RankedTipsCriteria()
    if arenaVisitor.gui.isEpicRandomBattle():
        return EpicRandomTipsCriteria()
    return EpicBattleTipsCriteria() if arenaVisitor.gui.isInEpicRange() else RandomTipsCriteria()


def getTipsIterator(arenaGuiType, battlesCount, vehicleType, vehicleNation, vehicleLvl):
    tipsItems = _getConditionedTips(arenaGuiType, battlesCount, vehicleType, vehicleNation, vehicleLvl)
    return rnd_choice_loop(*tipsItems) if tipsItems else None


class _ArenaGuiTypeCondition(namedtuple('_SquadExtra', ('mainPart', 'additionalPart'))):

    def validate(self, arenaGuiType):
        if self.mainPart == ALL:
            return True
        if self.mainPart == ANY:
            arenaGuiTypes = map(_getIntValue, self.additionalPart)
            return arenaGuiType in arenaGuiTypes
        if self.mainPart == EXCEPT:
            arenaGuiTypes = map(_getIntValue, self.additionalPart)
            return arenaGuiType not in arenaGuiTypes
        return False


_ArenaGuiTypeCondition.__new__.__defaults__ = (ALL, None)

def _getAddTipsKeysAndResourceID(res):
    result = []
    if res and res() != -1:
        while not res.exists():
            for key, nextRes in res.items():
                result.append(key)
                res = nextRes

        return (result, res())
    return (result, R.invalid())


def _readTips():
    result = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(list)))))
    tipsPattern = re.compile('^tip(\\d+)')
    for tipID, res in R.strings.tips.items():
        if tipID:
            sreMatch = tipsPattern.match(tipID)
            if sreMatch is not None and sreMatch.groups():
                keys, tipRes = _getAddTipsKeysAndResourceID(res)
                if len(keys) == TIPS_ADD_PATTERN_PARTS_COUNT:
                    status, group, battlesCountConds, arenaGuiType, vehicleTypeCondition, nation, vehLevel = keys
                    battlesCountConds = battlesCountConds.split('_')
                    if len(battlesCountConds) == BATTLE_CONDITIONS_PARTS_COUNT:
                        minBattlesCount = _getIntValue(battlesCountConds[1])
                        maxBattlesCount = _getIntValue(battlesCountConds[2])
                        if minBattlesCount is not None and maxBattlesCount is not None:
                            battleCondition = (minBattlesCount, maxBattlesCount)
                            arenaGuiTypeParts = arenaGuiType.split('_')
                            arenaGuiTypeCondition = _ArenaGuiTypeCondition(arenaGuiTypeParts[0], arenaGuiTypeParts[1:])
                            statusRes = R.strings.tips.dyn(status)()
                            icon = _getTipIconRes(tipID, group)
                            vehicleTypeCondition = vehicleTypeCondition.replace('_', '-')
                            for arenaGuiType in ARENA_GUI_TYPE.RANGE:
                                if arenaGuiTypeCondition.validate(arenaGuiType):
                                    result[battleCondition][arenaGuiType][vehicleTypeCondition][nation][vehLevel].append((statusRes, tipRes, icon))

    return result


def _readEpicTips():
    result = defaultdict(list)
    tipsPattern = re.compile('^epicTip(\\d+)')
    for tipID, res in R.strings.tips.items():
        if tipID:
            sreMatch = tipsPattern.match(tipID)
            if sreMatch is not None and sreMatch.groups():
                keys, tipRes = _getAddTipsKeysAndResourceID(res)
                if len(keys) == EPIC_TIPS_ADD_PATTERN_PARTS_COUNT:
                    status, battlesCountConditions = keys
                    battlesCountConditions = battlesCountConditions.split('_')
                    if len(battlesCountConditions) == BATTLE_CONDITIONS_PARTS_COUNT:
                        minBattlesCount = _getIntValue(battlesCountConditions[1])
                        maxBattlesCount = _getIntValue(battlesCountConditions[2])
                        if minBattlesCount is not None and maxBattlesCount is not None:
                            battleCondition = (minBattlesCount, maxBattlesCount)
                            result[battleCondition].append((R.strings.tips.dyn(status)(), tipRes, R.invalid()))

    return result


def _getTipIconRes(tipID, group):
    res = R.images.gui.maps.icons.battleLoading.tips.dyn(tipID)
    return res() if res.exists() else R.images.gui.maps.icons.battleLoading.groups.dyn(group)()


def _getIntValue(strCondition):
    if strCondition == INFINITY_STR_VALUE:
        return sys.maxint
    else:
        intValue = None
        try:
            intValue = int(strCondition)
        except ValueError:
            _logger.exception('Wrong strCondition, can not convert to int.')

        return intValue


_predefinedTips = _readTips()
_predefinedEpicTips = _readEpicTips()

def _getConditionedTips(arenaGuiType, battlesCount, vehicleType, vehicleNation, vehicleLvl):
    result = []
    battlesCountConditions = []
    for item in _predefinedTips.iteritems():
        (minBattlesCount, maxBattlesCount), _ = item
        if minBattlesCount <= battlesCount <= maxBattlesCount:
            battlesCountConditions.append(item)

    for _, vehicleTypeConditions in battlesCountConditions:
        for vehType in (vehicleType, ALL):
            for nation in (vehicleNation, ALL):
                for level in (str(vehicleLvl), ALL):
                    result.extend(vehicleTypeConditions[arenaGuiType][vehType][nation][level])

    return result


def _getEpicBattleConditionedTips(battlesCount):
    result = []
    battlesCountConditions = []
    for item in _predefinedEpicTips.iteritems():
        (minBattlesCount, maxBattlesCount), _ = item
        if minBattlesCount <= battlesCount <= maxBattlesCount:
            battlesCountConditions.append(item)

    for _, vehicleTypeConditions in battlesCountConditions:
        result.extend(vehicleTypeConditions)

    return result
