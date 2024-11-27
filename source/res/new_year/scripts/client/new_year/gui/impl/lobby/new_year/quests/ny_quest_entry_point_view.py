# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/quests/ny_quest_entry_point_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.quests.ny_quest_entry_point_view_model import NyQuestEntryPointViewModel
from new_year.gui.impl.lobby.new_year.tooltips.ny_quest_entrypoint_tooltip import NyQuestEntryPointTooltip
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.ny_constants import ViewAliases
from new_year.skeletons.new_year import INewYearController
from skeletons.gui.server_events import IEventsCache

class NYQuestEntryPointView(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.NYQuestEntryPointView(), flags=ViewFlags.VIEW, model=NyQuestEntryPointViewModel())
        self.__config = getNewYearGeneralConfig()
        self.__dailyPrefix = self.__config.getDailyPrefix()
        self.__weeklyPrefix = self.__config.getWeeklyPrefix()
        super(NYQuestEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NYQuestEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return NyQuestEntryPointTooltip() if event.contentID == R.views.new_year.lobby.new_year.tooltips.NYQuestEntryPointTooltip() else super(NYQuestEntryPointView, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        super(NYQuestEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.__eventsCache.onSyncCompleted, self.__updateModel), (self.__eventsCache.onProgressUpdated, self.__updateModel), (self.viewModel.onAction, self.__goToNYQuests))

    def __updateModel(self, *_):
        activeQuestCount = sum((1 for id, quest in self.__eventsCache.getAllQuests().items() if not quest.isCompleted() and quest.isStarted() and (id.startswith(self.__dailyPrefix) or id.startswith(self.__weeklyPrefix))))
        with self.viewModel.transaction() as ts:
            ts.setQuestsInProgress(activeQuestCount)

    def __goToNYQuests(self):
        NewYearNavigation.switchToView(ViewAliases.QUESTS_VIEW)
