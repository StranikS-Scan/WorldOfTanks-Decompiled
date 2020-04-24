# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/on_boarding_helper.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import TEN_YEARS_COUNTDOWN_ON_BOARDING_LAST_VISITED_BLOCK

def isOnBoardingCurrentBlockVisited(currentBlockNumber):
    lastVisitedBlock = AccountSettings.getSettings(TEN_YEARS_COUNTDOWN_ON_BOARDING_LAST_VISITED_BLOCK)
    return lastVisitedBlock == currentBlockNumber


def setOnBoardingLastVisitedBlock(currentBlockNumber):
    AccountSettings.setSettings(TEN_YEARS_COUNTDOWN_ON_BOARDING_LAST_VISITED_BLOCK, currentBlockNumber)
