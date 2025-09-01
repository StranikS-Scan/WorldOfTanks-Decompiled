# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/comp7_core_helpers/comp7_core_shared.py
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.periodic_battles.models import PeriodType, PrimeTimeStatus
from gui.shared.utils.SelectorBattleTypesUtils import isKnownBattleType
from helpers import time_utils
_SEASON_START_DURATION_DAYS = 7
_SEASON_END_DURATION_DAYS = 7

def getCurrentSeasonState(modeController, seasonStateClazz):
    currentTime = time_utils.getCurrentLocalServerTimestamp()
    periodInfo = modeController.getPeriodInfo()
    if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE):
        return seasonStateClazz.NOTSTARTED
    if periodInfo.periodType in (PeriodType.AFTER_SEASON,
     PeriodType.AFTER_CYCLE,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END):
        return seasonStateClazz.END
    if periodInfo.periodType == PeriodType.UNDEFINED:
        return seasonStateClazz.DISABLED
    if periodInfo.periodType == PeriodType.BETWEEN_SEASONS:
        return seasonStateClazz.END
    if periodInfo.cycleBorderLeft.delta(currentTime) < time_utils.ONE_DAY * _SEASON_START_DURATION_DAYS:
        return seasonStateClazz.JUSTSTARTED
    return seasonStateClazz.ENDSOON if periodInfo.cycleBorderRight.delta(currentTime) < time_utils.ONE_DAY * _SEASON_END_DURATION_DAYS else seasonStateClazz.ACTIVE


def getModeSeasonState(modeController, seasonStateClazz):
    startNotificationsPeriodLength = time_utils.ONE_DAY * 14
    endNotificationsPeriodLength = time_utils.ONE_DAY * 14
    currentTime = time_utils.getCurrentLocalServerTimestamp()
    periodInfo = modeController.getPeriodInfo()
    primeTimeStatus, _, _ = modeController.getPrimeTimeStatus()
    if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE, PeriodType.BETWEEN_SEASONS):
        return seasonStateClazz.NOTSTARTED
    if periodInfo.periodType in (PeriodType.AFTER_SEASON,
     PeriodType.AFTER_CYCLE,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.NOT_AVAILABLE_END,
     PeriodType.STANDALONE_NOT_AVAILABLE_END):
        return seasonStateClazz.END
    if periodInfo.periodType in (PeriodType.ALL_NOT_AVAILABLE, PeriodType.STANDALONE_NOT_AVAILABLE) or primeTimeStatus == PrimeTimeStatus.NOT_AVAILABLE:
        return seasonStateClazz.DISABLED
    if periodInfo.cycleBorderLeft.delta(currentTime) < startNotificationsPeriodLength:
        status = seasonStateClazz.JUSTSTARTED
    elif periodInfo.cycleBorderRight.delta(currentTime) < endNotificationsPeriodLength:
        status = seasonStateClazz.ENDSOON
    else:
        status = seasonStateClazz.ACTIVE
    return status


def getProgressionYearState(modeController, yearStateClazz):
    periodInfo = modeController.getPeriodInfo()
    hasNextSeason = modeController.getNextSeason() is not None
    hasPrevSeason = modeController.getPreviousSeason() is not None
    if periodInfo.periodType == PeriodType.BEFORE_SEASON:
        return yearStateClazz.NOTSTARTED
    elif periodInfo.periodType in (PeriodType.AFTER_SEASON,
     PeriodType.STANDALONE_NOT_AVAILABLE_END,
     PeriodType.ALL_NOT_AVAILABLE_END,
     PeriodType.NOT_AVAILABLE_END):
        return yearStateClazz.FINISHED
    else:
        return yearStateClazz.OFFSEASON if periodInfo.periodType == PeriodType.BETWEEN_SEASONS or periodInfo.periodType == PeriodType.AFTER_CYCLE and hasNextSeason or periodInfo.periodType == PeriodType.BEFORE_CYCLE and hasPrevSeason else yearStateClazz.ACTIVE


def getEventBannerState(modeController, seasonStateClazz, selectorBattleType):
    if not modeController.isAvailable():
        return EventBannerState.INACTIVE
    seasonState = getCurrentSeasonState(modeController, seasonStateClazz)
    if seasonState == seasonStateClazz.NOTSTARTED:
        return EventBannerState.ANNOUNCE
    primeTimeStatus, _, _ = modeController.getPrimeTimeStatus()
    if primeTimeStatus == PrimeTimeStatus.NOT_AVAILABLE:
        return EventBannerState.INACTIVE
    elif seasonState == seasonStateClazz.DISABLED:
        return EventBannerState.INACTIVE
    elif seasonState == seasonStateClazz.END:
        if modeController.getCurrentSeason(includePreannounced=True) is not None:
            return EventBannerState.ANNOUNCE
        return EventBannerState.INACTIVE
    else:
        return EventBannerState.IN_PROGRESS if isKnownBattleType(selectorBattleType) else EventBannerState.INTRO
