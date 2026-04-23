# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/quests_widget.py
import logging
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from historical_battles.gui.impl.gen.view_models.views.lobby.quests_widget_model import QuestsWidgetModel
from historical_battles.gui.impl.lobby.tooltips.quests_widget_tooltip import QuestsWidgetTooltip
from historical_battles.gui.server_events.battle_quests.quest_model_helpers import fillQuestModel, makeQuestModel
from historical_battles.gui.server_events.battle_quests.quests_container import HBQuestGroup
from historical_battles.gui.shared.event_dispatcher import showHBQuestsView
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.gui.quests_controller import IHBQuestsController
_logger = logging.getLogger(__name__)

class QuestsWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return QuestsWidgetView(R.views.historical_battles.lobby.QuestsWidget())


class QuestsWidgetView(ViewImpl):
    __slots__ = ()
    __gameEventController = dependency.descriptor(IGameEventController)
    __questsController = dependency.descriptor(IHBQuestsController)
    __DAILY_QUESTS_COUNT = 1
    __ALL_DAYS_QUESTS_COUNT = 2

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = QuestsWidgetModel()
        super(QuestsWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QuestsWidgetView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.QuestsWidgetTooltip():
            frontName = self.__gameEventController.frontController.getSelectedFront().getName()
            return QuestsWidgetTooltip(event.getArgument('questId'), frontName)
        return super(QuestsWidgetView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.__questsController.onQuestsUpdated, self.__onQuestsUpdated), (self.__questsController.onDailyQuestUpdate, self.__onQuestsUpdated), (self.viewModel.onClick, self.__onClick))

    def _onLoading(self, *args, **kwargs):
        super(QuestsWidgetView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__updateFront(model)
            self.__updateQuests(model)

    def __updateFront(self, model):
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        model.setFrontName(currentFront.getName())

    def __updateQuests(self, model):
        questsContainer = self.__questsController.getQuestsContainer()
        quests = questsContainer.getCurrentFrontQuestsByGroups(allowCompleted=True)
        questsModel = model.getQuests()
        questsModel.clear()
        for _, quest in quests[HBQuestGroup.DAILY][:self.__DAILY_QUESTS_COUNT]:
            questModel = makeQuestModel(quest, isDaily=True)
            questsModel.addViewModel(questModel)

        for _, quest in quests[HBQuestGroup.ALL_DAYS][:self.__ALL_DAYS_QUESTS_COUNT]:
            questModel = makeQuestModel(quest)
            questsModel.addViewModel(questModel)

        questsModel.invalidate()
        if quests[HBQuestGroup.SPECIAL]:
            _, specialQuest = quests[HBQuestGroup.SPECIAL][0]
            fillQuestModel(specialQuest, model.finalQuest)

    def __onQuestsUpdated(self):
        self.__updateModel()

    def __onClick(self):
        showHBQuestsView()
