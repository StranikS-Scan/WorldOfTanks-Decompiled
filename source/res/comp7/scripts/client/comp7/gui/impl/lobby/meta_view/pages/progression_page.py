# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/meta_view/pages/progression_page.py
import typing
from adisp import adisp_process
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, MetaRootViews, Rank
from comp7.gui.impl.gen.view_models.views.lobby.progression_item_model import ProgressionItemModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.progression_model import ProgressionModel
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers, comp7_shared, comp7_qualification_helpers
from comp7.gui.impl.lobby.meta_view import meta_view_helper
from comp7.gui.impl.lobby.meta_view.pages import PageSubModelPresenter
from comp7.gui.impl.lobby.tooltips.division_tooltip import DivisionTooltip
from comp7.gui.impl.lobby.tooltips.fifth_rank_tooltip import FifthRankTooltip
from comp7.gui.impl.lobby.tooltips.general_rank_tooltip import GeneralRankTooltip
from comp7.gui.impl.lobby.tooltips.last_update_tooltip import LastUpdateTooltip
from comp7.gui.impl.lobby.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
from comp7.gui.impl.lobby.tooltips.sixth_rank_tooltip import SixthRankTooltip
from comp7.gui.shared.event_dispatcher import showComp7MetaRootTab
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig

class ProgressionPage(PageSubModelPresenter):
    __slots__ = ('__lastUpdateTime',)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, viewModel, parentView):
        super(ProgressionPage, self).__init__(viewModel, parentView)
        self.__lastUpdateTime = None
        return

    @property
    def pageId(self):
        return MetaRootViews.PROGRESSION

    @property
    def viewModel(self):
        return super(ProgressionPage, self).getViewModel()

    @property
    def ranksConfig(self):
        return self.__comp7Controller.getRanksConfig()

    def initialize(self, **params):
        super(ProgressionPage, self).initialize(**params)
        self.__updateData()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7.mono.lobby.tooltips.general_rank_tooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.division_tooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'division': Division(event.getArgument('division')),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return DivisionTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.fifth_rank_tooltip():
            return FifthRankTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.sixth_rank_tooltip():
            return SixthRankTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.rank_inactivity_tooltip():
            return RankInactivityTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.last_update_tooltip():
            description = event.getArgument('description')
            return LastUpdateTooltip(description=description, updateTime=self.__lastUpdateTime)
        else:
            return None

    def _getEvents(self):
        return ((self.viewModel.qualificationModel.onRankRewardsPageOpen, self.__onRankRewardsPageOpen),
         (self.__comp7Controller.onRankUpdated, self.__updateData),
         (self.__comp7Controller.onModeConfigChanged, self.__updateData),
         (self.__comp7Controller.onComp7RanksConfigChanged, self.__updateData),
         (self.__comp7Controller.onQualificationBattlesUpdated, self.__updateData),
         (self.__comp7Controller.onQualificationStateUpdated, self.__updateData))

    def __updateData(self, *_):
        isQualification = self.__comp7Controller.isQualificationActive()
        if isQualification:
            self.__updateQualificationData()
        else:
            self.__updateProgressionData()

    def __updateQualificationData(self):
        with self.viewModel.transaction() as vm:
            comp7_qualification_helpers.setQualificationInfo(vm.qualificationModel)
            comp7_qualification_helpers.setQualificationBattles(vm.qualificationModel.getBattles())

    def __updateProgressionData(self, *_):
        with self.viewModel.transaction() as vm:
            vm.qualificationModel.setIsActive(False)
            vm.setRankInactivityCount(self.__comp7Controller.activityPoints)
            comp7_model_helpers.setElitePercentage(vm)
            self.__setCurrentScore(vm)
            self.__setItems(vm)
            self.__setLeaderBoardAsyncData()

    def __setCurrentScore(self, viewModel):
        currentScore = self.__comp7Controller.rating
        viewModel.setCurrentScore(currentScore)

    def __setItems(self, viewModel):
        itemsArray = viewModel.getItems()
        itemsArray.clear()
        for rank in self.ranksConfig.ranksOrder:
            itemModel = ProgressionItemModel()
            itemModel.setHasRankInactivity(comp7_shared.hasRankInactivity(rank))
            meta_view_helper.setProgressionItemData(itemModel, viewModel, rank, self.ranksConfig)
            itemsArray.addViewModel(itemModel)

        itemsArray.invalidate()

    @adisp_process
    def __setLeaderBoardAsyncData(self):
        self.viewModel.setIsLastBestUserPointsValueLoading(True)
        lbUpdateTime, isSuccess = yield self.__comp7Controller.leaderboard.getLastUpdateTime()
        if not self.isLoaded:
            return
        if isSuccess:
            self.__lastUpdateTime = lbUpdateTime
            self.viewModel.setLeaderboardUpdateTimestamp(lbUpdateTime or 0)
        lastRatingValue, isSuccess = yield self.__comp7Controller.leaderboard.getLastEliteRating()
        if not self.isLoaded:
            return
        if isSuccess:
            self.viewModel.setLastBestUserPointsValue(lastRatingValue or 0)
        self.viewModel.setIsLastBestUserPointsValueLoading(not isSuccess)

    def __onRankRewardsPageOpen(self):
        showComp7MetaRootTab(MetaRootViews.RANKREWARDS)
