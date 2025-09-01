# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/comp7_core_helpers/comp7_core_model_helpers.py
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_shared
from gui.periodic_battles.models import PrimeTimeStatus
from helpers.time_utils import getServerUTCTime

def isModeForcedDisabled(status, modeController):
    return not modeController.isAvailable() and status == PrimeTimeStatus.AVAILABLE


def setScheduleInfo(model, modeController, calendarDayTooltipID, seasonStateClazz, yearStateClazz, seasonNameClazz):
    season = getValidSeason(modeController)
    if season is not None:
        model.setTooltipId(calendarDayTooltipID)
    _SeasonPresenter.setSeasonInfo(model.season, modeController, seasonStateClazz, seasonNameClazz, season)
    yearState = comp7_core_shared.getProgressionYearState(modeController, yearStateClazz)
    model.year.setState(yearState)
    return


def getValidSeason(modeController, season=None):
    return season or _getCurrentSeason(modeController) or _getPreannouncedSeason(modeController) or _getPrevSeason(modeController) or _getNextSeason(modeController)


def getSeasonNameEnum(modeController, seasonNameClazz, season=None):
    season = getValidSeason(modeController, season)
    if season:
        seasonNameByNumber = {1: seasonNameClazz.FIRST,
         2: seasonNameClazz.SECOND,
         3: seasonNameClazz.THIRD}
        return seasonNameByNumber.get(season.getNumber())
    else:
        return None


def setSeasonInfo(model, modeController, seasonStateClazz, seasonNameClazz, season=None):
    season = getValidSeason(modeController, season)
    _SeasonPresenter.setSeasonInfo(model, modeController, seasonStateClazz, seasonNameClazz, season)


def _getCurrentSeason(modeController):
    return modeController.getCurrentSeason()


def _getPreannouncedSeason(modeController):
    return modeController.getPreannouncedSeason()


def _getNextSeason(modeController):
    return modeController.getNextSeason()


def _getPrevSeason(modeController):
    return modeController.getPreviousSeason()


class _SeasonPresenter(object):

    @classmethod
    def setSeasonInfo(cls, model, modeController, seasonStateClazz, seasonNameClazz, season):
        formattedServerTimestamp = round(getServerUTCTime())
        if season is not None:
            model.setName(getSeasonNameEnum(modeController, seasonNameClazz, season))
            model.setStartTimestamp(season.getStartDate())
            model.setEndTimestamp(season.getEndDate())
            model.setServerTimestamp(formattedServerTimestamp)
            model.setHasTentativeDates(season.hasTentativeDates())
        model.setState(cls.__getSeasonState(modeController, season, seasonStateClazz))
        return

    @staticmethod
    def __getSeasonState(modeController, season, seasonStateClazz):
        if season is not None:
            currentTime = getServerUTCTime()
            if currentTime < season.getStartDate():
                return seasonStateClazz.NOTSTARTED
            if currentTime > season.getEndDate():
                return seasonStateClazz.END
        return comp7_core_shared.getCurrentSeasonState(modeController, seasonStateClazz)
