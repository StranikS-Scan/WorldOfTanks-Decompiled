# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/widget/crew_banner_widget.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.crew_banner_widget_model import CrewBannerWidgetModel
from gui.impl.lobby.crew.crew_helpers.tankman_helpers import getPerksResetGracePeriod
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showResetAllPerksDialog, showFillAllPerksDialog
from gui.shared.gui_items.items_actions.actions import ResetAllTankmenSkillsAction, FillAllTankmenSkillsAction
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.crew_nps.loggers import CrewBannerWidgetLogger
from wg_async import wg_await, wg_async

class CrewBannerWidget(ViewImpl):
    LAYOUT_ID = R.views.lobby.crew.widgets.CrewBannerWidget
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__bannerLogger',)

    def __init__(self):
        settings = ViewSettings(self.LAYOUT_ID(), flags=ViewFlags.VIEW, model=CrewBannerWidgetModel())
        self.__bannerLogger = CrewBannerWidgetLogger()
        super(CrewBannerWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewBannerWidget, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onFill, self.__onFill), (self.viewModel.onReset, self.__onReset))

    def fillModel(self):
        with self.viewModel.transaction() as model:
            timeLeft = getPerksResetGracePeriod()
            model.setSecondsLeft(timeLeft)
            tsc = self.itemsCache.items.tankmenStatsCache
            model.setIsFillDisabled(not tsc.hasAnyTmanForFill())
            model.setIsResetDisabled(not tsc.hasAnyTmanForReset())

    @wg_async
    def __onFill(self):
        self.__bannerLogger.logFillButtonClick()
        result = yield wg_await(showFillAllPerksDialog())
        if result and result.result[0]:
            FillAllTankmenSkillsAction(result.result[1]).doAction()

    @wg_async
    def __onReset(self):
        self.__bannerLogger.logResetButtonClick()
        result = yield wg_await(showResetAllPerksDialog())
        if result.result[0]:
            ResetAllTankmenSkillsAction().doAction()
