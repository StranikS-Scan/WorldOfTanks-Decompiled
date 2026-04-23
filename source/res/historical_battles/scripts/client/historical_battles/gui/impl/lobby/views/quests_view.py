# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/quests_view.py
import logging
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.quests_view_model import QuestsViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_model import QuestModel
from historical_battles.gui.server_events.battle_quests.quest_model_helpers import fillQuestModel
from historical_battles.gui.server_events.battle_quests.quests_container import HBQuestGroup
from historical_battles.gui.server_events.hb_awards_formatter import HBQuestUIDataPacker
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.gui.quests_controller import IHBQuestsController
_logger = logging.getLogger(__name__)

class QuestsView(SubModelPresenter):
    __slots__ = ('__tooltipData',)
    __gameEventController = dependency.descriptor(IGameEventController)
    __questsController = dependency.descriptor(IHBQuestsController)
    __DAILY_QUESTS_COUNT = 1
    __ALL_DAYS_QUESTS_COUNT = 2

    def __init__(self, viewModel, parentView):
        super(QuestsView, self).__init__(viewModel, parentView)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(QuestsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(QuestsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipData.get(tooltipId) if tooltipId else None

    def initialize(self, *args, **kwargs):
        super(QuestsView, self).initialize(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.__questsController.onQuestsUpdated, self.__onQuestsUpdated), (self.__questsController.onDailyQuestUpdate, self.__onQuestsUpdated))

    def __updateModel(self):
        front = self.__gameEventController.frontController.getSelectedFront()
        questsContainer = self.__questsController.getQuestsContainer()
        quests = questsContainer.getCurrentFrontQuestsByGroups(allowCompleted=True)
        with self.viewModel.transaction() as model:
            model.setFrontName(front.getName())
            self.__tooltipData = {}
            self.__fillQuests(model.getQuests(), quests[HBQuestGroup.DAILY], quests[HBQuestGroup.ALL_DAYS])
            self.__fillSpecialQuest(model.finalQuest, quests[HBQuestGroup.SPECIAL])

    def __fillQuests(self, questsModel, dailyQuests, allDaysQuests):
        questsModel.clear()
        dailyQuests = dailyQuests[:self.__DAILY_QUESTS_COUNT]
        for _, quest in dailyQuests:
            questModel = QuestModel()
            self.__packQuest(quest, questModel, isDaily=True)
            questsModel.addViewModel(questModel)

        allDaysQuests = allDaysQuests[:self.__ALL_DAYS_QUESTS_COUNT]
        for _, quest in allDaysQuests:
            questModel = QuestModel()
            self.__packQuest(quest, questModel, isDaily=False)
            questsModel.addViewModel(questModel)

        questsModel.invalidate()

    def __fillSpecialQuest(self, questModel, specialQuests):
        if not specialQuests:
            return
        _, quest = specialQuests[0]
        self.__packQuest(quest, questModel)

    def __packQuest(self, quest, questModel, isDaily=False):
        questPacker = HBQuestUIDataPacker(quest, initialTooltipIndex=len(self.__tooltipData))
        fillQuestModel(quest, questModel, isDaily=isDaily, questPacker=questPacker)
        self.__tooltipData.update(questPacker.getTooltipData())

    def __onQuestsUpdated(self):
        self.__updateModel()
