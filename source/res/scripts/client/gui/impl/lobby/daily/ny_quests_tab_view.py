# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/ny_quests_tab_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.ny_quests_tab_view_model import NyQuestsTabViewModel
from gui.impl.lobby.daily import NYTabs
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from new_year.skeletons.new_year import INewYearController
from new_year.gui.game_control.ny_controller import isAllNyQuestsCompleted

class NYQuestTabView(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    TAB_CONST = NYTabs.DAILY

    def __init__(self, layoutID=None):
        settings = ViewSettings(R.views.lobby.daily.NyQuestsTabView())
        settings.model = NyQuestsTabViewModel()
        super(NYQuestTabView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        self.__update()
        super(NYQuestTabView, self)._onLoading()

    def _getEvents(self):
        return ((self.__nyController.onStateChanged, self.__update),)

    def __update(self):
        with self.getViewModel().transaction() as ts:
            isEnabled = self.__nyController.isEnabled()
            ts.setIsBlocked(not isEnabled)
            ts.setIsCompleted(isEnabled and isAllNyQuestsCompleted(self.__eventsCache))
