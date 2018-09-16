# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/tips.py
import re
import sys
from collections import defaultdict, namedtuple
from constants import ARENA_GUI_TYPE
import constants
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TIPS import TIPS
from gui.shared.utils.functions import rnd_choice_loop
from helpers import dependency
from helpers import i18n
from debug_utils import LOG_CURRENT_EXCEPTION
from items.vehicles import VEHICLE_CLASS_TAGS
import nations
from skeletons.gui.battle_session import IBattleSessionProvider
ALL = 'all'
ANY = 'any'
EXCEPT = 'except'
INFINITY_STR_VALUE = 'infinity'
TIPS_IMAGE_SOURCE = '../maps/icons/battleLoading/tips/%s.png'
TIPS_GROUPS_SOURCE = '../maps/icons/battleLoading/groups/%s.png'
TIPS_PATTERN_PARTS_COUNT = 8
EPIC_TIPS_PATTERN_PARTS_COUNT = 3
BATTLE_CONDITIONS_PARTS_COUNT = 2
_FoundTip = namedtuple('_FoundTip', 'status, body, icon')

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
            tip = _FoundTip('', '', '')
        return tip


class EpicBattleTipsCriteria(RandomTipsCriteria):

    def find(self):
        iterator = self.__getTipsIterator(self._count)
        if iterator is not None:
            tip = _FoundTip(*next(iterator))
        else:
            tip = _FoundTip('', '', '')
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
        return _FoundTip(i18n.makeString('#tips:howToPlay'), i18n.makeString('#tips:sandbox%s' % geometryIndex), TIPS_IMAGE_SOURCE % ('sandbox' + str(geometryIndex) + str(positionIndex)))


def _getEventTipIterator():
    tipSize = len(RES_ICONS.MAPS_ICONS_BATTLELOADING_TIPS_EVENT_ENUM)
    if tipSize > 0:
        items = range(tipSize)
        return rnd_choice_loop(*items)
    else:
        return None


class EventTipsCriteria(_TipsCriteria):
    __tipIterator = None

    def __init__(self):
        super(EventTipsCriteria, self).__init__()
        if EventTipsCriteria.__tipIterator is None:
            EventTipsCriteria.__tipIterator = _getEventTipIterator()
        return

    def find(self):
        iterator = EventTipsCriteria.__tipIterator
        if iterator is not None:
            tipNum = next(iterator)
            return _FoundTip(i18n.makeString(TIPS.getEventTipTitle(tipNum)), i18n.makeString(TIPS.getEventTipBody(tipNum)), RES_ICONS.getEventBattleLoadingTipImage(tipNum))
        else:
            return _FoundTip('', '', '')


def _getRankedTipIterator():
    tipSize = len(RES_ICONS.MAPS_ICONS_BATTLELOADING_TIPS_RANKED_ENUM)
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
            return _FoundTip(i18n.makeString(TIPS.getRankedTipTittle(tipNum)), i18n.makeString(TIPS.getRankedTipBody(tipNum)), RES_ICONS.getRankedBattleLoadingTipImage(tipNum))
        else:
            return _FoundTip('', '', '')


def _getEpicRandomTipIterator():
    tipSize = len(RES_ICONS.MAPS_ICONS_BATTLELOADING_TIPS_EPICRANDOM_ENUM)
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
            return _FoundTip(i18n.makeString(TIPS.getEpicRandomTipTitle(tipNum)), i18n.makeString(TIPS.getEpicRandomTipBody(tipNum)), RES_ICONS.getEpicRandomBattleLoadingTipImage(tipNum))
        else:
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

def _readTips():
    result = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(list)))))
    tipsPattern = re.compile('^tip(\\d+)')
    try:
        translator = i18n.g_translators['tips']
    except IOError:
        LOG_CURRENT_EXCEPTION()
        return result

    for key in translator._catalog.iterkeys():
        if key:
            sreMatch = tipsPattern.match(key)
            if sreMatch is not None and sreMatch.groups():
                strTipsConditions = key.split('/')
                if len(strTipsConditions) == TIPS_PATTERN_PARTS_COUNT:
                    tipID, status, group, battlesCountConditions, arenaGuiType, vehicleTypeCondition, nation, vehLevel = strTipsConditions
                    battlesCountConditions = battlesCountConditions.split('_')
                    if len(battlesCountConditions) == BATTLE_CONDITIONS_PARTS_COUNT:
                        minBattlesCount = _getIntValue(battlesCountConditions[0])
                        maxBattlesCount = _getIntValue(battlesCountConditions[1])
                        if minBattlesCount is not None and maxBattlesCount is not None:
                            battleCondition = (minBattlesCount, maxBattlesCount)
                            arenaGuiTypeParts = arenaGuiType.split('_')
                            arenaGuiTypeCondition = _ArenaGuiTypeCondition(arenaGuiTypeParts[0], arenaGuiTypeParts[1:])
                            for arenaGuiType in ARENA_GUI_TYPE.RANGE:
                                if arenaGuiTypeCondition.validate(arenaGuiType):
                                    result[battleCondition][arenaGuiType][vehicleTypeCondition][nation][vehLevel].append((i18n.makeString('#tips:%s' % status), i18n.makeString('#tips:%s' % key), _getTipIcon(tipID, group)))

    i18n.g_translators.clear()
    return result


def _readEpicTips():
    result = defaultdict(list)
    tipsPattern = re.compile('^epicTip(\\d+)')
    try:
        translator = i18n.g_translators['tips']
    except IOError:
        LOG_CURRENT_EXCEPTION()
        return result

    for key in translator._catalog.iterkeys():
        if key:
            sreMatch = tipsPattern.match(key)
            if sreMatch is not None and sreMatch.groups():
                strTipsConditions = key.split('/')
                if len(strTipsConditions) == EPIC_TIPS_PATTERN_PARTS_COUNT:
                    _, status, battlesCountConditions = strTipsConditions
                    battlesCountConditions = battlesCountConditions.split('_')
                    if len(battlesCountConditions) == BATTLE_CONDITIONS_PARTS_COUNT:
                        minBattlesCount = _getIntValue(battlesCountConditions[0])
                        maxBattlesCount = _getIntValue(battlesCountConditions[1])
                        if minBattlesCount is not None and maxBattlesCount is not None:
                            battleCondition = (minBattlesCount, maxBattlesCount)
                            result[battleCondition].append((i18n.makeString('#tips:%s' % status), i18n.makeString('#tips:%s' % key), ''))

    return result


def _getTipIcon(tipID, group):
    currentTipImage = TIPS_IMAGE_SOURCE % tipID
    return currentTipImage if currentTipImage in RES_ICONS.MAPS_ICONS_BATTLELOADING_TIPS_ENUM else TIPS_GROUPS_SOURCE % group


def _getIntValue(strCondition):
    if strCondition == INFINITY_STR_VALUE:
        return sys.maxint
    else:
        intValue = None
        try:
            intValue = int(strCondition)
        except ValueError:
            LOG_CURRENT_EXCEPTION()

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
