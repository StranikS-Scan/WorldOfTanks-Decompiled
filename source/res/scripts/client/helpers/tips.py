# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/tips.py
import logging
import random
import re
import sys
from collections import namedtuple
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import WATCHED_PRE_BATTLE_TIPS_SECTION
from constants import ARENA_GUI_TYPE
from gui.doc_loaders.prebattle_tips_loader import getPreBattleTipsConfig
from gui.impl.gen import R
from gui.battle_pass.battle_pass_helpers import isBattlePassActiveSeason
from helpers import dependency
from gui.shared.utils.functions import replaceHyphenToUnderscore
from skeletons.gui.battle_session import IBattleSessionProvider
_TipData = namedtuple('_BattleLoadingTipData', 'status, body, icon')
_logger = logging.getLogger(__name__)
_SANDBOX_GEOMETRY_INDEX = ('100_thepit', '10_hills')
_RANDOM_TIPS_PATTERN = '^(tip\\d+)'
_EPIC_BATTLE_TIPS_PATTERN = '^(epicTip\\d+)'
_EPIC_RANDOM_TIPS_PATTERN = '^(epicRandom\\d+)'
_RANKED_BATTLES_TIPS_PATTERN = '^(ranked\\d+)'
_BATTLE_ROYALE_TIPS_PATTERN = '^(battleRoyale\\d+$)'

class _BattleLoadingTipPriority(object):
    GENERIC = 1
    PRECEDING = 2


class _TipsCriteria(object):
    __slots__ = ('_battlesCount', '_vehicleType')

    def __init__(self):
        super(_TipsCriteria, self).__init__()
        self._battlesCount = 0
        self._vehicleType = None
        return

    def setBattleCount(self, count):
        self._battlesCount = count

    def setVehicleType(self, vehicleType):
        self._vehicleType = vehicleType

    def find(self):
        foundTip = self._findRandomTip()
        if foundTip is not None:
            foundTip.markWatched()
            return foundTip.getData()
        else:
            return _TipData(R.invalid(), R.invalid(), R.invalid())

    def _findRandomTip(self):
        suitableTips = filter(self._suitableTipPredicate, self._getTargetList())
        precedingTips = [ tip for tip in suitableTips if tip.getPriority() == _BattleLoadingTipPriority.PRECEDING ]
        foundTip = None
        if precedingTips:
            foundTip = random.choice(precedingTips)
        elif suitableTips:
            foundTip = random.choice(suitableTips)
        return foundTip

    def _getArenaGuiType(self):
        return None

    def _suitableTipPredicate(self, tip):
        return False if tip is None else tip.test(self._getArenaGuiType(), self._battlesCount, self._vehicleType)

    def _getTargetList(self):
        _logger.error('Method _getTargetList has to be overridden')
        return []


class _RandomTipsCriteria(_TipsCriteria):

    def _getTargetList(self):
        return _randomTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.RANDOM


class _EpicBattleTipsCriteria(_TipsCriteria):

    def find(self):
        tipData = super(_EpicBattleTipsCriteria, self).find()
        return _TipData(tipData.status, tipData.body, R.invalid())

    def _getTargetList(self):
        return _epicBattleTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.EPIC_BATTLE


class _SandboxTipsCriteria(_TipsCriteria):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

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
        return _TipData(R.strings.tips.howToPlay(), R.strings.tips.dyn('sandbox{}'.format(geometryIndex))(), R.images.gui.maps.icons.battleLoading.tips.dyn(iconKey)())


class _EventTipsCriteria(_TipsCriteria):

    def find(self):
        return _TipData(R.strings.tips.eventTitle(), R.strings.tips.eventMessage(), R.images.gui.maps.icons.battleLoading.tips.event())


class _RankedTipsCriteria(_TipsCriteria):

    def _getTargetList(self):
        return _rankedTips


class _EpicRandomTipsCriteria(_TipsCriteria):

    def _getTargetList(self):
        return _epicRandomTips


class BattleRoyaleTipsCriteria(_TipsCriteria):

    def __init__(self, arenaVisitor):
        super(BattleRoyaleTipsCriteria, self).__init__()
        self._arenaVisitor = arenaVisitor

    def find(self):
        foundTip = self._findRandomTip()
        if foundTip is not None:
            foundTip.markWatched()
            tipData = foundTip.getData()
            geometryName = replaceHyphenToUnderscore(self._arenaVisitor.getArenaType().geometryName)
            geomertyIconResId = _tryGetTipIconRes('_'.join((foundTip.getTipId(), geometryName)))
            if geomertyIconResId != R.invalid():
                tipData = _TipData(tipData.status, tipData.body, geomertyIconResId)
            return tipData
        else:
            return _TipData(R.invalid(), R.invalid(), R.invalid())

    def _getTargetList(self):
        return _battleRoyaleTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.BATTLE_ROYALE


def getTipsCriteria(arenaVisitor):
    if arenaVisitor.gui.isSandboxBattle():
        return _SandboxTipsCriteria()
    if arenaVisitor.gui.isEventBattle():
        return _EventTipsCriteria()
    if arenaVisitor.gui.isRankedBattle():
        return _RankedTipsCriteria()
    if arenaVisitor.gui.isEpicRandomBattle():
        return _EpicRandomTipsCriteria()
    if arenaVisitor.gui.isInEpicRange():
        return _EpicBattleTipsCriteria()
    return BattleRoyaleTipsCriteria(arenaVisitor) if arenaVisitor.gui.isBattleRoyale() else _RandomTipsCriteria()


def _readTips(pattern):
    result = []
    tipsPattern = re.compile(pattern)
    for tipID, descriptionResId in R.strings.tips.items():
        if tipID:
            reMatch = tipsPattern.match(tipID)
            if reMatch is not None:
                if tipID not in _tipsConfig:
                    _logger.error('Tips by tipID(%s) not in prebattle_tips.xml', tipID)
                else:
                    result.append(_buildBattleLoadingTip(tipID, descriptionResId()))

    return result


def _buildBattleLoadingTip(tipID, descriptionResID):
    tipConfig = _tipsConfig.get(tipID)
    tipFilter = tipConfig.get('filter')
    if tipFilter is not None and tipFilter['preceding'] is not None:
        tip = _PrecedingBattleLoadingTip()
        tip.setShowLimit(tipFilter['preceding']['showTimes'])
    else:
        tip = _BattleLoadingTip()
    tip.build(tipID, descriptionResID, tipConfig)
    return tip


def _getTipIconRes(tipID, group):
    res = R.images.gui.maps.icons.battleLoading.tips.dyn(tipID)
    return res() if res.exists() else R.images.gui.maps.icons.battleLoading.groups.dyn(group)()


def _tryGetTipIconRes(tipID):
    res = R.images.gui.maps.icons.battleLoading.tips.dyn(tipID)
    return res() if res.exists() else R.invalid()


class _BattleLoadingTip(object):
    __slots__ = ('_arenaTypes', '_battlesLimit', '_requiredTags', '_nation', '_level', '_vehicleClass', 'priority', '_tipId', '_statusResId', '_iconResId', '_descriptionResId', '_battlePassCheck')

    def __init__(self):
        super(_BattleLoadingTip, self).__init__()
        self._tipId = None
        self._statusResId = R.invalid()
        self._iconResId = R.invalid()
        self._descriptionResId = R.invalid()
        self._battlesLimit = (0, sys.maxint)
        self._requiredTags = _SubsetValidator()
        self._arenaTypes = _ValueValidator()
        self._level = _ValueValidator()
        self._nation = _ValueValidator()
        self._vehicleClass = _ValueValidator()
        self._battlePassCheck = _BattlePassValidator()
        return

    def build(self, tipID, descriptionResID, config):
        if config is not None:
            self._statusResId = R.strings.tips.dyn(config['status'])()
            self._iconResId = _getTipIconRes(tipID, config['group'])
            tipFilter = config['filter']
            if tipFilter is not None:
                self._battlesLimit = (tipFilter['minBattles'], tipFilter['maxBattles'])
                self._requiredTags.update(tipFilter['tags'])
                self._arenaTypes.update(tipFilter['arenaTypes'])
                self._level.update(tipFilter['levels'])
                self._nation.update(tipFilter['nations'])
                self._vehicleClass.update(tipFilter['vehicleClass'])
                self._battlePassCheck.update(tipFilter['battlePassActiveCheck'])
        self._tipId = tipID
        self._descriptionResId = descriptionResID
        return

    def markWatched(self):
        pass

    def getPriority(self):
        return _BattleLoadingTipPriority.GENERIC

    def getTipId(self):
        return self._tipId

    def getData(self):
        return _TipData(self._statusResId, self._descriptionResId, self._iconResId)

    def test(self, arenaGuiType, battlesCount, vehicleType):
        minBattles, maxBattles = self._battlesLimit
        return minBattles <= battlesCount <= maxBattles and self._requiredTags.validate(vehicleType.tags) and self._arenaTypes.validate(arenaGuiType) and self._level.validate(vehicleType.level) and self._nation.validate(nations.NAMES[vehicleType.nationID]) and self._vehicleClass.validate(vehicleType.classTag) and self._battlePassCheck.validate()


class _PrecedingBattleLoadingTip(_BattleLoadingTip):
    __slots__ = ('_showLimit', '_watchedTimes')

    def __init__(self):
        super(_PrecedingBattleLoadingTip, self).__init__()
        self._showLimit = 0

    def setShowLimit(self, limit):
        self._showLimit = limit

    def markWatched(self):
        _increaseTipWatchedCounter(self._tipId)

    def getPriority(self):
        watchedTimes = _getTipWatchedCounter(self._tipId)
        return _BattleLoadingTipPriority.PRECEDING if watchedTimes < self._showLimit else _BattleLoadingTipPriority.GENERIC


class _ValueValidator(object):
    __slots__ = ('_possibleValues',)

    def __init__(self):
        super(_ValueValidator, self).__init__()
        self._possibleValues = frozenset()

    def update(self, values):
        self._possibleValues = frozenset(values.split())

    def validate(self, value):
        return True if not self._possibleValues else str(value) in self._possibleValues


class _BattlePassValidator(object):
    __slots__ = ('_checkBattlePass',)

    def __init__(self):
        super(_BattlePassValidator, self).__init__()
        self._checkBattlePass = False

    def update(self, value):
        self._checkBattlePass = bool(value)

    def validate(self):
        return isBattlePassActiveSeason() if self._checkBattlePass else True


class _SubsetValidator(_ValueValidator):

    def validate(self, targetValues):
        return True if not self._possibleValues else self._possibleValues.issubset(targetValues)


def _getTipWatchedCounter(tipID):
    cache = _getWatchedCache()
    return cache.get(tipID, 0)


def _increaseTipWatchedCounter(tipID):
    cache = _getWatchedCache()
    counter = cache.get(tipID, 0)
    cache[tipID] = counter + 1
    AccountSettings.setSettings(WATCHED_PRE_BATTLE_TIPS_SECTION, cache)


def _getWatchedCache():
    global _watchedTipsCache
    if _watchedTipsCache is None:
        _watchedTipsCache = AccountSettings.getSettings(WATCHED_PRE_BATTLE_TIPS_SECTION)
    return _watchedTipsCache


_watchedTipsCache = None
_tipsConfig = getPreBattleTipsConfig()
_randomTips = _readTips(_RANDOM_TIPS_PATTERN)
_rankedTips = _readTips(_RANKED_BATTLES_TIPS_PATTERN)
_epicBattleTips = _readTips(_EPIC_BATTLE_TIPS_PATTERN)
_epicRandomTips = _readTips(_EPIC_RANDOM_TIPS_PATTERN)
_battleRoyaleTips = _readTips(_BATTLE_ROYALE_TIPS_PATTERN)
