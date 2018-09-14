# Embedded file name: scripts/client/helpers/tips.py
import re
import sys
from collections import defaultdict, namedtuple
from constants import ARENA_GUI_TYPE
import constants
from gui.battle_control import arena_info
from gui.shared.utils.functions import rnd_choice_loop
from helpers import i18n
from debug_utils import LOG_CURRENT_EXCEPTION
from items.vehicles import VEHICLE_CLASS_TAGS
import nations
ALL = 'all'
ANY = 'any'
EXCEPT = 'except'
INFINITY_STR_VALUE = 'infinity'
TIPS_IMAGE_SOURCE = '../maps/icons/battleLoading/tips/%s.png'
TIPS_GROUPS_SOURCE = '../maps/icons/battleLoading/groups/%s.png'
TIPS_PATTERN_PARTS_COUNT = 8
BATTLE_CONDITIONS_PARTS_COUNT = 2
_FoundTip = namedtuple('_FoundTip', 'status, body')

class _TipsCriteria(object):
    __slots__ = ('_count', '_classTag', '_nation', '_level')

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
        raise tag in VEHICLE_CLASS_TAGS or AssertionError
        self._classTag = tag
        return self

    def getNation(self):
        return self._nation

    def setNation(self, nation):
        raise nation in nations.NAMES or AssertionError
        self._nation = nation
        return self

    def getLevel(self):
        return self._level

    def setLevel(self, level):
        raise 0 < level < 11 or AssertionError
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
            tip = _FoundTip('', '')
        return tip


class SandboxTipsCriteria(_TipsCriteria):

    def find(self):
        return _FoundTip(i18n.makeString('#tips:howToPlay'), i18n.makeString('#tips:sandbox01'))


def getTipsCriteria(arena):
    if arena_info.isInSandboxBattle(arena):
        return SandboxTipsCriteria()
    else:
        return RandomTipsCriteria()


def getTipsIterator(arenaGuiType, battlesCount, vehicleType, vehicleNation, vehicleLvl):
    tipsItems = _getConditionedTips(arenaGuiType, battlesCount, vehicleType, vehicleNation, vehicleLvl)
    if len(tipsItems) > 0:
        return rnd_choice_loop(*tipsItems)
    else:
        return None


class _ArenaGuiTypeCondition(namedtuple('_SquadExtra', ('mainPart', 'additionalPart'))):

    def validate(self, arenaGuiType):
        if self.mainPart == ALL:
            return True
        elif self.mainPart == ANY:
            arenaGuiTypes = map(_getIntValue, self.additionalPart)
            return arenaGuiType in arenaGuiTypes
        elif self.mainPart == EXCEPT:
            arenaGuiTypes = map(_getIntValue, self.additionalPart)
            return arenaGuiType not in arenaGuiTypes
        else:
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
        if len(key) > 0:
            sreMatch = tipsPattern.match(key)
            if sreMatch is not None and len(sreMatch.groups()) > 0:
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
                                    result[battleCondition][arenaGuiType][vehicleTypeCondition][nation][vehLevel].append((i18n.makeString('#tips:%s' % status), i18n.makeString('#tips:%s' % key)))

    return result


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
        return


_predefinedTips = _readTips()

def _getConditionedTips(arenaGuiType, battlesCount, vehicleType, vehicleNation, vehicleLvl):
    result = []
    battlesCountConditions = filter(lambda ((minBattlesCount, maxBattlesCount), item): minBattlesCount <= battlesCount <= maxBattlesCount, _predefinedTips.iteritems())
    for _, vehicleTypeConditions in battlesCountConditions:
        for vehType in (vehicleType, ALL):
            for nation in (vehicleNation, ALL):
                for level in (str(vehicleLvl), ALL):
                    result.extend(vehicleTypeConditions[arenaGuiType][vehType][nation][level])

    return result
