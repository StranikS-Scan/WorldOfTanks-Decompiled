# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/progression/progression.py
import typing
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.gen.view_models.views.lobby.battle_results.progression.progression_model import ProgressionModel
from gui.server_events.events_helpers import isDailyQuest
from gui.shared.missions.packers.events import DailyQuestUIDataPacker
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class ProgressionSubPresenter(BattleResultsSubPresenter):
    __eventsCache = dependency.descriptor(IEventsCache)

    @classmethod
    def getViewModelType(cls):
        return ProgressionModel

    def packBattleResults(self, battleResults):
        allCommonQuests = self.__eventsCache.getQuests()
        allCommonQuests.update(self.__eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
        progress = battleResults.reusable.personal.getQuestsProgress()
        questsWithProgress = [ allCommonQuests[qID] for qID in allCommonQuests if qID in progress ]
        self.__packDailyQuests(self.getViewModel(), battleResults, questsWithProgress)

    def __packDailyQuests(self, vm, battleResults, quests):
        dailyQuests = (q for q in quests if isDailyQuest(q.getID()))
        vmList = vm.getDailyQuests()
        vmList.clear()
        for quest in dailyQuests:
            packer = DailyQuestUIDataPacker(quest)
            model = packer.pack()
            vmList.addViewModel(model)

        vmList.invalidate()
