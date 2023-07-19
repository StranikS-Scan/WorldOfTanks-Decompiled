# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/prebattle_tips_loader.py
import sys
import resource_helper
_PREBATTLE_TIPS_XML_PATH = 'gui/prebattle_tips.xml'
_PRECEDING_DEFAULT_SHOW_TIMES = 1
DEFAULT_STATUS = 'payAttention'
DEFAULT_GROUP = 'all'
_OPTIONAL_FILTER_FLAGS = ('isBattlePassActiveSeason', 'isRankedYearRewardEnabled', 'isRankedLeaderboardEnabled', 'isRankedShopEnabled', 'isPostProgressionEnabled')

def _readPreBattleTips():
    filters = dict()
    tips = dict()
    ctx, root = resource_helper.getRoot(_PREBATTLE_TIPS_XML_PATH)
    for _, filterSection in resource_helper.getIterator(ctx, root['filters']):
        filterId = filterSection.readString('id')
        filters[filterId] = {'minBattles': filterSection.readInt('minBattles', 0),
         'maxBattles': filterSection.readInt('maxBattles', sys.maxint),
         'arenaTypes': _readPossibleValues(filterSection, 'arenaTypes'),
         'nations': _readPossibleValues(filterSection, 'nations'),
         'levels': _readPossibleValues(filterSection, 'levels'),
         'vehicleClass': _readPossibleValues(filterSection, 'vehicleClass'),
         'tags': _readPossibleValues(filterSection, 'tags'),
         'realms': _readPossibleValues(filterSection, 'realms'),
         'preceding': _readPrecedingData(filterSection),
         'chassisType': filterSection.readInt('chassisType', -1)}
        for key in _OPTIONAL_FILTER_FLAGS:
            if filterSection.has_key(key):
                filters[filterId][key] = filterSection.readBool(key)

    for _, tipsSection in resource_helper.getIterator(ctx, root['tips']):
        filterId = tipsSection.readString('filter')
        tipId = tipsSection.readString('id')
        status = tipsSection.readString('status', DEFAULT_STATUS)
        group = tipsSection.readString('group', DEFAULT_GROUP)
        tipConfig = filters.get(filterId)
        tips[tipId] = {'filter': tipConfig,
         'status': status,
         'group': group}

    resource_helper.purgeResource(_PREBATTLE_TIPS_XML_PATH)
    return tips


def _readPossibleValues(filterSection, key):
    return frozenset(filterSection.readString(key).split())


def _readPrecedingData(section):
    precedingData = None
    if section['preceding'] is not None:
        precedingData = {'showTimes': section['preceding'].readInt('showTimes', _PRECEDING_DEFAULT_SHOW_TIMES)}
    return precedingData


def getPreBattleTipsConfig():
    global _preBattleTipsConfig
    if _preBattleTipsConfig is None:
        _preBattleTipsConfig = _readPreBattleTips()
    return _preBattleTipsConfig


_preBattleTipsConfig = None
