# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/tips.py
import logging
import random
import re
from collections import namedtuple
import nations
from account_helpers import AccountSettings
from account_helpers.AccountSettings import WATCHED_PRE_BATTLE_TIPS_SECTION
from constants import ARENA_GUI_TYPE
from gui.battle_pass.battle_pass_helpers import isBattlePassActiveSeason
from gui.doc_loaders.prebattle_tips_loader import getPreBattleTipsConfig
from gui.impl.gen import R
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.system_factory import registerBattleTipCriteria, registerBattleTipsCriteria, collectBattleTipsCriteria
from helpers import dependency
from realm import CURRENT_REALM
from skeletons.gui.game_control import IRankedBattlesController, IVehiclePostProgressionController
_logger = logging.getLogger(__name__)
_RANDOM_TIPS_PATTERN = '^(tip\\d+)'
_EPIC_BATTLE_TIPS_PATTERN = '^(epicTip\\d+)'
_EPIC_RANDOM_TIPS_PATTERN = '^(epicRandom\\d+)'
_RANKED_BATTLES_TIPS_PATTERN = '^(ranked\\d+)'
_BATTLE_ROYALE_TIPS_PATTERN = '^(battleRoyale\\d+$)'
_COMP7_TIPS_PATTERN = '^(comp7\\d+$)'
_WINBACK_TIPS_PATTERN = '^(winback\\d+$)'
_MAPBOX_TIPS_PATTERN = '^(mapbox\\d+)'

class _BattleLoadingTipPriority(object):
    GENERIC = 1
    PRECEDING = 2


class TipData(namedtuple('_BattleLoadingTipData', 'status, body, icon')):

    def isValid(self):
        return self.status != R.invalid() or self.body != R.invalid() or self.icon != R.invalid()


class TipsCriteria(object):
    __slots__ = ('_ctx', '_tipsValidator')

    def __init__(self, *_):
        super(TipsCriteria, self).__init__()
        self._ctx = {'arenaType': self._getArenaGuiType()}
        self._tipsValidator = self._getTipsValidator()

    def setContext(self, ctx):
        self._ctx.update(ctx)
        _logger.info('Tips context for battle: %s', self._ctx)

    def find(self):
        foundTip = self._findRandomTip()
        if foundTip is not None:
            foundTip.markWatched()
            return foundTip.getData()
        else:
            return TipData(R.invalid(), R.invalid(), R.invalid())

    def _findRandomTip(self):
        suitableTips = filter(self._suitableTipPredicate, self._getTargetList())
        precedingTips = [ tip for tip in suitableTips if tip.getPriority() == _BattleLoadingTipPriority.PRECEDING ]
        if _logger.isEnabledFor(logging.INFO):
            _logger.info('Suitable preceding tips: %s', precedingTips)
            _logger.info('Suitable tips: %s', suitableTips)
        foundTip = None
        if precedingTips:
            foundTip = random.choice(precedingTips)
        elif suitableTips:
            foundTip = random.choice(suitableTips)
        return foundTip

    def _getArenaGuiType(self):
        return None

    def _getTipsValidator(self):
        return _TipsValidator()

    def _suitableTipPredicate(self, tip):
        return False if tip is None or self._tipsValidator is None else self._tipsValidator.validateRegularTip(tipFilter=tip.tipFilter, ctx=self._ctx)

    def _getTargetList(self):
        _logger.error('Method _getTargetList has to be overridden')
        return []


class _RandomTipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _randomTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.RANDOM


class _EpicBattleTipsCriteria(TipsCriteria):

    def find(self):
        tipData = super(_EpicBattleTipsCriteria, self).find()
        return TipData(tipData.status, tipData.body, R.invalid())

    def _getTargetList(self):
        return _epicBattleTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.EPIC_BATTLE


class _EventTipsCriteria(TipsCriteria):

    def find(self):
        return TipData(R.strings.tips.eventTitle(), R.strings.tips.eventMessage(), R.images.gui.maps.icons.battleLoading.tips.event())


class _RankedTipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _rankedTips


class _EpicRandomTipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _epicRandomTips


class _Comp7TipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _comp7Tips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.COMP7


class _WinbackTipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _winbackTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.WINBACK


class BattleRoyaleTipsCriteria(TipsCriteria):

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
                tipData = TipData(tipData.status, tipData.body, geomertyIconResId)
            return tipData
        else:
            return TipData(R.invalid(), R.invalid(), R.invalid())

    def _getTargetList(self):
        return _battleRoyaleTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.BATTLE_ROYALE


class _MapboxTipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _mapboxTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.MAPBOX


registerBattleTipCriteria(ARENA_GUI_TYPE.EVENT_BATTLES, _EventTipsCriteria)
registerBattleTipCriteria(ARENA_GUI_TYPE.RANKED, _RankedTipsCriteria)
registerBattleTipCriteria(ARENA_GUI_TYPE.BATTLE_ROYALE, BattleRoyaleTipsCriteria)
registerBattleTipCriteria(ARENA_GUI_TYPE.COMP7, _Comp7TipsCriteria)
registerBattleTipCriteria(ARENA_GUI_TYPE.WINBACK, _WinbackTipsCriteria)
registerBattleTipCriteria(ARENA_GUI_TYPE.MAPBOX, _MapboxTipsCriteria)
registerBattleTipsCriteria(ARENA_GUI_TYPE.EPIC_RANGE, _EpicBattleTipsCriteria)
registerBattleTipsCriteria((ARENA_GUI_TYPE.EPIC_RANDOM, ARENA_GUI_TYPE.EPIC_RANDOM_TRAINING), _EpicRandomTipsCriteria)

def getTipsCriteria(arenaVisitor):
    criteriaCls = collectBattleTipsCriteria(arenaVisitor.gui.guiType)
    return _RandomTipsCriteria() if criteriaCls is None else criteriaCls(arenaVisitor)


def readTips(pattern):
    result = []
    tipsPattern = re.compile(pattern)
    for tipID, descriptionResId in R.strings.tips.items():
        if tipID:
            reMatch = tipsPattern.match(tipID)
            if reMatch is not None:
                if tipID not in _tipsConfig:
                    _logger.warning('Tips by tipID(%s) not in prebattle_tips.xml', tipID)
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


class _TipsValidator(object):

    def __init__(self):
        super(_TipsValidator, self).__init__()
        self._validatorsList = (_BattlesValidator(),
         _ArenaGuiTypeValidator(),
         _TagsValidator(),
         _LevelValidator(),
         _NationValidator(),
         _VehicleClassValidator(),
         _RealmsValidator(),
         _BattlePassValidator(),
         _RankedBattlesValidator(),
         _PostProgressionValidator(),
         _ChassisTypeValidator())

    def validateRegularTip(self, tipFilter, ctx=None):
        if not tipFilter:
            return True
        for validator in self._validatorsList:
            if not validator.validate(tipFilter, ctx):
                return False

        return True


class _BattleLoadingTip(object):
    __slots__ = ('_tipId', '_statusResId', '_iconResId', '_descriptionResId', '_tipFilter')

    def __init__(self):
        super(_BattleLoadingTip, self).__init__()
        self._tipId = None
        self._statusResId = R.invalid()
        self._iconResId = R.invalid()
        self._descriptionResId = R.invalid()
        self._tipFilter = None
        return

    def build(self, tipID, descriptionResID, config):
        if config is not None:
            self._statusResId = R.strings.tips.dyn(config['status'])()
            self._iconResId = _getTipIconRes(tipID, config['group'])
            self._tipFilter = config['filter']
        self._tipId = tipID
        self._descriptionResId = descriptionResID
        return

    @property
    def tipFilter(self):
        return self._tipFilter

    def markWatched(self):
        pass

    def getPriority(self):
        return _BattleLoadingTipPriority.GENERIC

    def getTipId(self):
        return self._tipId

    def getData(self):
        return TipData(self._statusResId, self._descriptionResId, self._iconResId)

    def __repr__(self):
        return self._tipId


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


class _ChassisTypeValidator(object):

    @staticmethod
    def validate(tipFilter, ctx):
        chassisType = tipFilter['chassisType']
        return chassisType < 0 or ctx['vehicleType'].chassisType == chassisType


class _BattlesValidator(object):

    @staticmethod
    def validate(tipFilter, ctx):
        battlesCount = ctx.get('battlesCount')
        minBattles, maxBattles = tipFilter['minBattles'], tipFilter['maxBattles']
        return minBattles <= battlesCount <= maxBattles


class _ArenaGuiTypeValidator(object):

    @staticmethod
    def validate(tipFilter, ctx):
        expected = tipFilter['arenaTypes']
        actual = ctx['arenaType']
        return not expected or actual in expected


class _TagsValidator(object):

    @staticmethod
    def validate(tipFilter, ctx):
        requiredTags = tipFilter['tags']
        tags = ctx['vehicleType'].tags
        return not requiredTags or requiredTags.issubset(tags)


class _LevelValidator(object):

    @staticmethod
    def validate(tipFilter, ctx):
        possibleLevels = tipFilter['levels']
        level = ctx['vehicleType'].level
        return not possibleLevels or str(level) in possibleLevels


class _NationValidator(object):

    @staticmethod
    def validate(tipFilter, ctx):
        possibleNations = tipFilter['nations']
        nation = nations.NAMES[ctx['vehicleType'].nationID]
        return not possibleNations or nation in possibleNations


class _VehicleClassValidator(object):

    @staticmethod
    def validate(tipFilter, ctx):
        possibleClasses = tipFilter['vehicleClass']
        vehicleClassTag = ctx['vehicleType'].classTag
        return not possibleClasses or vehicleClassTag in possibleClasses


class _RealmsValidator(object):

    @staticmethod
    def validate(tipFilter, _):
        possibleRealms = tipFilter['realms']
        return not possibleRealms or CURRENT_REALM in possibleRealms


class _BattlePassValidator(object):
    __slots__ = ('_isActiveSeason',)

    def __init__(self):
        super(_BattlePassValidator, self).__init__()
        self._isActiveSeason = isBattlePassActiveSeason()

    def validate(self, tipFilter, _):
        return tipFilter['isBattlePassActiveSeason'] == self._isActiveSeason if 'isBattlePassActiveSeason' in tipFilter else True


class _RankedBattlesValidator(object):
    __slots__ = ('_isYearRewardEnabled', '_isLeaderboardEnabled', '_isShopEnabled', '_isLeagueRewardEnabled')
    _rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(_RankedBattlesValidator, self).__init__()
        self._isYearRewardEnabled = self._rankedController.isYearRewardEnabled()
        self._isLeaderboardEnabled = self._rankedController.isYearLBEnabled()
        self._isShopEnabled = self._rankedController.isRankedShopEnabled()
        self._isLeagueRewardEnabled = self._rankedController.isLeagueRewardEnabled()

    def validate(self, tipFilter, _):
        if 'isRankedYearRewardEnabled' in tipFilter:
            if tipFilter['isRankedYearRewardEnabled'] != self._isYearRewardEnabled:
                return False
        if 'isRankedLeaderboardEnabled' in tipFilter:
            if tipFilter['isRankedLeaderboardEnabled'] != self._isLeaderboardEnabled:
                return False
        if 'isRankedShopEnabled' in tipFilter:
            if tipFilter['isRankedShopEnabled'] != self._isShopEnabled:
                return False
        if 'isRankedLeagueRewardEnabled' in tipFilter:
            if tipFilter['isRankedLeagueRewardEnabled'] != self._isLeagueRewardEnabled:
                return False
        return True


class _PostProgressionValidator(object):
    __slots__ = ('_isPostProgressionEnabled',)
    _postProgressionCtrl = dependency.descriptor(IVehiclePostProgressionController)

    def __init__(self):
        super(_PostProgressionValidator, self).__init__()
        self._isPostProgressionEnabled = self._postProgressionCtrl.isEnabled()

    def validate(self, tipFilter, _):
        return tipFilter['isPostProgressionEnabled'] == self._isPostProgressionEnabled if 'isPostProgressionEnabled' in tipFilter else True


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
_randomTips = readTips(_RANDOM_TIPS_PATTERN)
_rankedTips = readTips(_RANKED_BATTLES_TIPS_PATTERN)
_epicBattleTips = readTips(_EPIC_BATTLE_TIPS_PATTERN)
_epicRandomTips = readTips(_EPIC_RANDOM_TIPS_PATTERN)
_battleRoyaleTips = readTips(_BATTLE_ROYALE_TIPS_PATTERN)
_comp7Tips = readTips(_COMP7_TIPS_PATTERN)
_winbackTips = readTips(_WINBACK_TIPS_PATTERN)
_mapboxTips = readTips(_MAPBOX_TIPS_PATTERN)
