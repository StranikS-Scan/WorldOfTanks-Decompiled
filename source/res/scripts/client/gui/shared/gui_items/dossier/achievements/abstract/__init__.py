# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/__init__.py
from helpers import dependency
from mixins import Deprecated
from mixins import Quest
from mixins import HasVehiclesList as _HasVehiclesList
from mixins import NoProgressBar
from ClassProgressAchievement import ClassProgressAchievement
from HistoricalAchievement import HistoricalAchievement
from NationSpecificAchievement import NationSpecificAchievement
from RareAchievement import RareAchievement
from RegularAchievement import RegularAchievement
from SeriesAchievement import SeriesAchievement
from SimpleProgressAchievement import SimpleProgressAchievement
from skeletons.gui.server_events import IEventsCache

class DeprecatedAchievement(Deprecated, RegularAchievement):
    pass


class QuestAchievement(Quest, RegularAchievement):
    pass


class DeprecatedClassAchievement(Deprecated, NoProgressBar, ClassProgressAchievement):
    pass


def isRareAchievement(achievement):
    return isinstance(achievement, RareAchievement)


def isSeriesAchievement(achievement):
    return isinstance(achievement, SeriesAchievement)


def achievementHasVehiclesList(achievement):
    return isinstance(achievement, _HasVehiclesList)


def getCompletedPotapovQuestsCount(seasonID, vehClasses):
    eventsCache = dependency.instance(IEventsCache)

    def _filter(quest):
        return quest.isFullCompleted() and len(vehClasses & quest.getVehicleClasses())

    result = 0
    for tile in eventsCache.random.getSeasons()[seasonID].getTiles().itervalues():
        result += len(tile.getQuestsByFilter(_filter))

    return result


__all__ = ['ClassProgressAchievement',
 'HistoricalAchievement',
 'NationSpecificAchievement',
 'RareAchievement',
 'RegularAchievement',
 'SeriesAchievement',
 'SimpleProgressAchievement',
 'DeprecatedAchievement',
 'QuestAchievement',
 'isRareAchievement',
 'isSeriesAchievement',
 'achievementHasVehiclesList']
