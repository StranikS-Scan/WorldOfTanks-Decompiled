# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/progression_page.py
import typing
from adisp import adisp_process
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progression_item_model import ProgressionItemModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progression_item_model import Type
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progression_model import ProgressionModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_division import Division
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import Rank
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.lobby.comp7 import comp7_model_helpers, comp7_shared
from gui.impl.lobby.comp7.meta_view import meta_view_helper
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.impl.lobby.comp7.tooltips.division_tooltip import DivisionTooltip
from gui.impl.lobby.comp7.tooltips.general_rank_tooltip import GeneralRankTooltip
from gui.impl.lobby.comp7.tooltips.last_update_tooltip import LastUpdateTooltip
from gui.impl.lobby.comp7.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
from gui.impl.lobby.comp7.tooltips.seventh_rank_tooltip import SeventhRankTooltip
from gui.impl.lobby.comp7.tooltips.sixth_rank_tooltip import SixthRankTooltip
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from helpers.server_settings import Comp7PrestigeRanksConfig

class ProgressionPage(PageSubModelPresenter):
    __slots__ = ('__lastUpdateTime',)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

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
        return self.__lobbyCtx.getServerSettings().comp7PrestigeRanksConfig

    def initialize(self, *args, **kwargs):
        super(ProgressionPage, self).initialize(*args, **kwargs)
        self.__updateData()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.comp7.tooltips.GeneralRankTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.lobby.comp7.tooltips.DivisionTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'division': Division(event.getArgument('division')),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return DivisionTooltip(params=params)
        elif contentID == R.views.lobby.comp7.tooltips.SixthRankTooltip():
            return SixthRankTooltip()
        elif contentID == R.views.lobby.comp7.tooltips.SeventhRankTooltip():
            return SeventhRankTooltip()
        elif contentID == R.views.lobby.comp7.tooltips.RankInactivityTooltip():
            return RankInactivityTooltip()
        elif contentID == R.views.lobby.comp7.tooltips.LastUpdateTooltip():
            description = event.getArgument('description')
            return LastUpdateTooltip(description=description, updateTime=self.__lastUpdateTime)
        else:
            return None

    def _getEvents(self):
        return ((self.__comp7Controller.onRankUpdated, self.__updateData), (self.__comp7Controller.onComp7ConfigChanged, self.__updateData), (self.__comp7Controller.onComp7RanksConfigChanged, self.__updateData))

    def __updateData(self, *_):
        with self.viewModel.transaction() as vm:
            comp7_model_helpers.setRanksInfo(vm)
            self.__setCurrentScore(vm)
            self.__setItems(vm)
            self.__setLeaderBoardAsyncData()

    def __setCurrentScore(self, viewModel):
        currentScore = self.__comp7Controller.rating
        viewModel.setCurrentScore(currentScore)
        viewModel.setMaxScore(currentScore)

    def __setItems(self, viewModel):
        itemsArray = viewModel.getItems()
        itemsArray.clear()
        for rankIdx, _ in enumerate(self.ranksConfig.ranksOrder):
            itemModel = ProgressionItemModel()
            itemModel.setType(Type.RANK)
            itemModel.setHasRankInactivity(comp7_shared.hasRankInactivity(rankIdx))
            meta_view_helper.setProgressionItemData(itemModel, viewModel, rankIdx, self.ranksConfig)
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
        self.viewModel.setIsLastBestUserPointsValueLoading(False)
