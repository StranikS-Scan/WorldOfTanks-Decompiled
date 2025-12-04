# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/quests/ny_quest_helper.py
from helpers import time_utils
from helpers.time_utils import ONE_WEEK
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year_common.items.components.ny_constants import CurrentNYConstants

def getWeekFromStart():
    return int(time_utils.getServerUTCTime() - getNewYearGeneralConfig().getNewYearStartDate()) / ONE_WEEK


def getCurrentWeek():
    return max(1, min(getWeekFromStart() + 1, CurrentNYConstants.MAX_CELEB_TEXTS))
