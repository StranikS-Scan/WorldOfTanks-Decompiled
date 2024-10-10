# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/common.py
import typing
from gui.battle_results.presenter.events import event
from gui.battle_results.presenter.events.battle_pass import getBattlePassEvents
from gui.battle_results.presenter.events.quests import getQuestsEvents
from gui.battle_results.presenter.events.ranked import getRankedEvents
from gui.battle_results.presenter.events.research import getResearchEvents
from gui.server_events.events_helpers import EventInfoModel
from skeletons.gui.game_control import IQuestsController
from gui.server_events.events_constants import WT_BOSS_GROUP_ID
from white_tiger.gui.impl.lobby.wt_quests_view import HUNTER_QUEST_CHAINS
from constants import WT_TEAMS
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.events_stats_model import EventsStatsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

def _getEventsDataProviders():
    return [getRankedEvents,
     getBattlePassEvents,
     getQuestsEvents,
     getResearchEvents,
     event.getEvents]


def setEventsData(model, tooltipData, reusable, result):
    dataProviders = _getEventsDataProviders()
    for provider in dataProviders:
        dataItems = provider(tooltipData, reusable, result)
        if dataItems is None:
            continue
        for data in dataItems:
            model.getEvents().addViewModel(data)

    with model.transaction() as mod:
        _setHasQuestsToShowState(mod, reusable)
        mod.setQuestsUpdateTimeLeft(EventInfoModel.getDailyProgressResetTimeDelta())
        mod.setIsHunter(reusable.getPersonalTeam() == WT_TEAMS.HUNTERS_TEAM)
    return


def _setHasQuestsToShowState(model, reusable):
    isBoss = reusable.getPersonalTeam() == WT_TEAMS.BOSS_TEAM
    currentQuests = _getCurrentQuests([WT_BOSS_GROUP_ID]) if isBoss else _getCurrentQuests(HUNTER_QUEST_CHAINS)
    progressData = reusable.progress.getQuestsProgress()
    isAllQuestsCompletedBeforeBattle = all((quest.isCompleted() and qID not in progressData for qID, quest in currentQuests))
    model.setHasQuestsToShow(not isAllQuestsCompletedBeforeBattle)


def _getCurrentQuests(groupIDs):
    questController = dependency.instance(IQuestsController)

    def filterFunc(quest):
        return quest.isEventBattlesQuest() and quest.getGroupID() in groupIDs and (quest.isCompleted() or quest.accountReqs.isAvailable())

    quests = questController.eventsCache.getAllQuests(filterFunc).items()
    return quests
