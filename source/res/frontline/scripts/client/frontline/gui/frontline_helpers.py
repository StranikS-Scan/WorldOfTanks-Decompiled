# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/frontline_helpers.py
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_container_tab_model import TabType
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import time_utils, dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def geFrontlineState(withPrimeTime=False, epicController=None):
    now = time_utils.getCurrentLocalServerTimestamp()
    startDate, endDate = epicController.getSeasonTimeRange()
    if now > endDate:
        season = epicController.getCurrentSeason()
        endSeasonDate = season.getEndDate() if season else 0
        return (FrontlineState.FINISHED, endSeasonDate, int(endSeasonDate - now))
    if now < startDate:
        return (FrontlineState.ANNOUNCE, startDate, int(startDate - now))
    primeTimeStatus, timeLeft, _ = epicController.getPrimeTimeStatus()
    if primeTimeStatus is not PrimeTimeStatus.AVAILABLE:
        if withPrimeTime:
            return (FrontlineState.FROZEN, int(now + timeLeft), timeLeft)
        return (FrontlineState.FROZEN, endDate, int(endDate - now))
    return (FrontlineState.ACTIVE, endDate, int(endDate - now))


def getStatesUnavailableForHangar():
    return [FrontlineState.FINISHED, FrontlineState.ANNOUNCE]


def getProperTabWhileHangarUnavailable():
    frontlineState, _, _ = geFrontlineState()
    return TabType.REWARDS if frontlineState == FrontlineState.FINISHED else None


def isHangarAvailable():
    frontlineState, _, _ = geFrontlineState()
    return frontlineState not in getStatesUnavailableForHangar()
