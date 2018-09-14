# Embedded file name: scripts/client/helpers/tips.py
import re
import sys
import random
from collections import defaultdict
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.utils.functions import rnd_choice_loop
from helpers import i18n
from debug_utils import LOG_CURRENT_EXCEPTION
ALL = 'all'
INFINITY_STR_VALUE = 'infinity'
TIPS_IMAGE_SOURCE = '../maps/icons/battleLoading/tips/%s.png'
TIPS_GROUPS_SOURCE = '../maps/icons/battleLoading/groups/%s.png'
TIPS_PATTERN_PARTS_COUNT = 7
BATTLE_CONDITIONS_PARTS_COUNT = 2

def getTipsIterator(battlesCount, vehicleType, vehicleNation, vehicleLvl):
    tipsItems = _getConditionedTips(battlesCount, vehicleType, vehicleNation, vehicleLvl)
    if len(tipsItems) > 0:
        return rnd_choice_loop(*tipsItems)
    else:
        return None


def _readTips():
    result = defaultdict(lambda : defaultdict(lambda : defaultdict(lambda : defaultdict(list))))
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
                    tipID, status, group, battlesCountConditions, vehicleTypeCondition, nation, vehLevel = strTipsConditions
                    battlesCountConditions = battlesCountConditions.split('_')
                    if len(battlesCountConditions) == BATTLE_CONDITIONS_PARTS_COUNT:
                        minBattlesCount = _getIntValue(battlesCountConditions[0])
                        maxBattlesCount = _getIntValue(battlesCountConditions[1])
                        if minBattlesCount is not None and maxBattlesCount is not None:
                            battleCondition = (minBattlesCount, maxBattlesCount)
                            result[battleCondition][vehicleTypeCondition][nation][vehLevel].append((i18n.makeString('#tips:%s' % status), i18n.makeString('#tips:%s' % key), _getTipIcon(tipID, group)))

    return result


def _getTipIcon(tipID, group):
    currentTipImage = TIPS_IMAGE_SOURCE % tipID
    if currentTipImage in RES_ICONS.MAPS_ICONS_BATTLELOADING_TIPS_ENUM:
        return currentTipImage
    return TIPS_GROUPS_SOURCE % group


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

def _getConditionedTips(battlesCount, vehicleType, vehicleNation, vehicleLvl):
    result = []
    battlesCountConditions = filter(lambda ((minBattlesCount, maxBattlesCount), item): minBattlesCount <= battlesCount <= maxBattlesCount, _predefinedTips.iteritems())
    for _, vehicleTypeConditions in battlesCountConditions:
        for vehType in (vehicleType, ALL):
            for nation in (vehicleNation, ALL):
                for level in (str(vehicleLvl), ALL):
                    result.extend(vehicleTypeConditions[vehType][nation][level])

    return result
