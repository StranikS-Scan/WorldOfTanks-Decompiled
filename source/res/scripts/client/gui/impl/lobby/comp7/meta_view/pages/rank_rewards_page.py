# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/rank_rewards_page.py
import logging
from collections import namedtuple
from functools import partial
import typing
from shared_utils import first
from comp7_common import Comp7QuestType
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.rank_rewards_item_model import RankRewardsItemModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.rank_rewards_model import RankRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import Rank
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.comp7 import comp7_model_helpers, comp7_shared
from gui.impl.lobby.comp7.comp7_bonus_packer import packRanksRewardsQuestBonuses
from gui.impl.lobby.comp7.comp7_c11n_helpers import getStylePreviewVehicle, getPreviewOutfit
from gui.impl.lobby.comp7.comp7_quest_helpers import parseComp7RanksQuestID, parseComp7PeriodicQuestID, isComp7VisibleQuest, getComp7QuestType
from gui.impl.lobby.comp7.meta_view.meta_view_helper import setProgressionItemData, getRankDivisions
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.impl.lobby.comp7.tooltips.fifth_rank_tooltip import FifthRankTooltip
from gui.impl.lobby.comp7.tooltips.general_rank_tooltip import GeneralRankTooltip
from gui.impl.lobby.comp7.tooltips.sixth_rank_tooltip import SixthRankTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.vehicles import makeVehicleTypeCompDescrByName
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from gui.impl.gen.view_models.views.lobby.comp7.comp7_style_bonus_model import Comp7StyleBonusModel
    from gui.impl.gen.view_models.views.lobby.comp7.qualification_model import QualificationModel
    from gui.server_events.event_items import TokenQuest
    from helpers.server_settings import Comp7RanksConfig
_logger = logging.getLogger(__name__)
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))
_DEFAULT_PREVIEW_VEHICLE = 'uk:GB91_Super_Conqueror'

class RankRewardsPage(PageSubModelPresenter):
    __slots__ = ('__bonusData', '__rankQuests', '__periodicQuests')
    __itemsCache = dependency.descriptor(IItemsCache)
    __c11nService = dependency.descriptor(ICustomizationService)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, viewModel, parentView):
        super(RankRewardsPage, self).__init__(viewModel, parentView)
        self.__rankQuests = {}
        self.__periodicQuests = {}
        self.__bonusData = {}

    @property
    def pageId(self):
        return MetaRootViews.RANKREWARDS

    @property
    def viewModel(self):
        return super(RankRewardsPage, self).getViewModel()

    @property
    def ranksConfig(self):
        return self.__lobbyCtx.getServerSettings().comp7RanksConfig

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            rank = event.getArgument('rank')
            if tooltipId is not None and rank is not None:
                bonusData = self.__bonusData[int(rank)][int(tooltipId)]
                if bonusData is not None:
                    window = BackportTooltipWindow(bonusData.tooltip, self.parentView.getParentWindow())
                    window.load()
                    return window
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            fromIndex = int(event.getArgument('fromIndex'))
            rank = int(event.getArgument('rank'))
            bonuses = [ d.bonus for d in self.__bonusData[rank][fromIndex:] ]
            return AdditionalRewardsTooltip(bonuses)
        elif contentID == R.views.lobby.comp7.tooltips.GeneralRankTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.lobby.comp7.tooltips.FifthRankTooltip():
            return FifthRankTooltip()
        else:
            return SixthRankTooltip() if contentID == R.views.lobby.comp7.tooltips.SixthRankTooltip() else None

    def initialize(self, index=None, *args, **kwargs):
        super(RankRewardsPage, self).initialize()
        if index is None:
            index = RankRewardsModel.DEFAULT_ITEM_INDEX
        with self.viewModel.transaction() as tx:
            tx.setInitialItemIndex(index)
            comp7_model_helpers.setElitePercentage(tx)
            self.__updateQuests()
            self.__setRanksData(tx)
            self.__setQualificationState(tx.qualificationModel)
        return

    def finalize(self):
        self.__rankQuests.clear()
        self.__periodicQuests.clear()
        self.__bonusData.clear()
        super(RankRewardsPage, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onPreviewOpen, self.__onPreviewOpen),
         (self.__eventsCache.onSyncCompleted, self.__onEventsSyncCompleted),
         (self.__comp7Controller.onComp7RanksConfigChanged, self.__onRanksConfigChanged),
         (self.__comp7Controller.onRankUpdated, self.__onRankUpdated),
         (self.__comp7Controller.onQualificationStateUpdated, self.__onQualificationStateUpdated))

    def __updateQuests(self):
        comp7Quests = self.__eventsCache.getAllQuests(lambda q: isComp7VisibleQuest(q.getID())).values()
        self.__rankQuests = self.__parseQuestsByDivision(comp7Quests, parseComp7RanksQuestID, Comp7QuestType.RANKS)
        self.__periodicQuests = self.__parseQuestsByDivision(comp7Quests, parseComp7PeriodicQuestID, Comp7QuestType.PERIODIC)

    def __setRanksData(self, model):
        itemsArray = model.getItems()
        itemsArray.clear()
        for rank in self.ranksConfig.ranksOrder:
            itemModel = RankRewardsItemModel()
            self.__setRank(itemModel, rank)
            itemsArray.addViewModel(itemModel)

        itemsArray.invalidate()

    def __setRank(self, itemModel, rank):
        divisions = getRankDivisions(rank, self.ranksConfig)
        division = first(divisions)
        setProgressionItemData(itemModel, self.viewModel, rank, self.ranksConfig)
        self.__setRankRewards(itemModel, division)

    def __setRankRewards(self, itemModel, division):
        rankQuest = self.__rankQuests.get(division.dvsnID)
        periodicQuest = self.__periodicQuests.get(division.dvsnID)
        if rankQuest is None:
            _logger.error('Missing Competitive7x7 Rank Quests for division %s.', division)
            return
        else:
            itemModel.setHasRewardsReceived(rankQuest.isCompleted())
            bonuses, tooltips = packRanksRewardsQuestBonuses(rankQuest, periodicQuest)
            bonusData = zip(bonuses, tooltips)
            rank = comp7_shared.getRankEnumValue(division)
            self.__bonusData[rank] = self.__setRewards(itemModel, bonusData)
            return

    def __setQualificationState(self, qualificationModel):
        qualificationModel.setIsActive(self.__comp7Controller.isQualificationActive())

    def __onEventsSyncCompleted(self):
        with self.viewModel.transaction() as tx:
            self.__updateQuests()
            self.__setRanksData(tx)

    def __onRanksConfigChanged(self):
        with self.viewModel.transaction() as tx:
            comp7_model_helpers.setElitePercentage(tx)
            self.__setRanksData(tx)

    def __onRankUpdated(self, *_, **__):
        with self.viewModel.transaction() as tx:
            self.__setRanksData(tx)

    def __onQualificationStateUpdated(self):
        self.__setQualificationState(self.viewModel.qualificationModel)

    @args2params(int, int)
    def __onPreviewOpen(self, rank, index):
        bonus = first(self.__bonusData[rank]).bonus
        style = self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, bonus.getStyleID())
        vehicleCD = getStylePreviewVehicle(style, makeVehicleTypeCompDescrByName(_DEFAULT_PREVIEW_VEHICLE))
        outfit = getPreviewOutfit(style, bonus.getBranchID(), bonus.getProgressLevel())
        showStylePreview(vehicleCD, style, backCallback=partial(shared_events.showComp7MetaRootView, self.pageId, index), outfit=outfit)

    @staticmethod
    def __setRewards(itemModel, bonusData):
        packedBonusData = []
        rewards = itemModel.getRewards()
        rewards.clear()
        for idx, (packedBonus, tooltipData) in enumerate(bonusData):
            packedBonus.setTooltipId(str(idx))
            rewards.addViewModel(packedBonus)
            packedBonusData.append(_BonusData(packedBonus, tooltipData))

        rewards.invalidate()
        return packedBonusData

    @staticmethod
    def __parseQuestsByDivision(quests, parser, questType):
        result = {}
        for q in quests:
            if getComp7QuestType(q.getID()) != questType:
                continue
            division = parser(q.getID())
            if division is not None:
                result[division.dvsnID] = q
            _logger.error('Division number could not be parsed - %s', q.getID())

        return result
