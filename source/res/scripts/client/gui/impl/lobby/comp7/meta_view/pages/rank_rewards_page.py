# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/rank_rewards_page.py
import logging
import typing
from collections import namedtuple
from CurrentVehicle import g_currentVehicle
from comp7_common import Comp7QuestType
from gui.impl.lobby.comp7.comp7_c11n_helpers import getComp7ProgressionStyleCamouflage
from items.vehicles import VehicleDescriptor
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.rank_rewards_model import RankRewardsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.rank_rewards_item_model import RankRewardsItemModel, RankRewardsState
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_item_base_model import Rank
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.comp7.meta_view.meta_view_helper import setRankData, setDivisionData, getRankDivisions
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.impl.lobby.comp7 import comp7_model_helpers, comp7_shared
from gui.impl.lobby.comp7.comp7_bonus_packer import packRanksRewardsQuestBonuses
from gui.impl.lobby.comp7.comp7_quest_helpers import parseComp7RanksQuestID, parseComp7PeriodicQuestID, isComp7Quest, getComp7QuestType
from gui.impl.lobby.comp7.tooltips.general_rank_tooltip import GeneralRankTooltip
from gui.impl.lobby.comp7.tooltips.seventh_rank_tooltip import SeventhRankTooltip
from gui.impl.lobby.comp7.tooltips.sixth_rank_tooltip import SixthRankTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showStylePreview, hideVehiclePreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from gui.impl.gen.view_models.views.lobby.comp7.comp7_style_bonus_model import Comp7StyleBonusModel
    from gui.server_events.event_items import TokenQuest
    from gui.shared.gui_items.customization.c11n_items import Style
    from helpers.server_settings import Comp7PrestigeRanksConfig
    from vehicle_outfit.outfit import Outfit
_logger = logging.getLogger(__name__)
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))
_DEFAULT_PREVIEW_VEHICLE_TYPE = 'uk:GB91_Super_Conqueror'

class RankRewardsPage(PageSubModelPresenter):
    __slots__ = ('__bonusData', '__rankQuests', '__periodicQuests')
    __itemsCache = dependency.descriptor(IItemsCache)
    __c11nService = dependency.descriptor(ICustomizationService)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
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
        return self.__lobbyCtx.getServerSettings().comp7PrestigeRanksConfig

    def _getEvents(self):
        return ((self.viewModel.onPreviewOpen, self.__onPreviewOpen),
         (self.__eventsCache.onSyncCompleted, self.__onEventsSyncCompleted),
         (self.__comp7Controller.onComp7RanksConfigChanged, self.__onRanksConfigChanged),
         (self.__comp7Controller.onRankUpdated, self.__onRankUpdated))

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
            showCount = int(event.getArgument('showCount'))
            rank = int(event.getArgument('rank'))
            bonuses = [ d.bonus for d in self.__bonusData[rank][showCount:] ]
            return AdditionalRewardsTooltip(bonuses)
        elif contentID == R.views.lobby.comp7.tooltips.GeneralRankTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.lobby.comp7.tooltips.SixthRankTooltip():
            return SixthRankTooltip()
        else:
            return SeventhRankTooltip() if contentID == R.views.lobby.comp7.tooltips.SeventhRankTooltip() else None

    def initialize(self, index=None, *args, **kwargs):
        super(RankRewardsPage, self).initialize()
        if index is None:
            index = RankRewardsModel.DEFAULT_ITEM_INDEX
        with self.viewModel.transaction() as tx:
            tx.setInitialItemIndex(index)
            comp7_model_helpers.setElitePercentage(tx)
            self.__updateQuests()
            self.__setRanksData(tx)
        return

    def finalize(self):
        self.__rankQuests.clear()
        self.__periodicQuests.clear()
        self.__bonusData.clear()
        super(RankRewardsPage, self).finalize()

    def __updateQuests(self):
        comp7Quests = self.__eventsCache.getAllQuests(lambda q: isComp7Quest(q.getID())).values()
        self.__rankQuests = self.__parseQuestsByDivision(comp7Quests, parseComp7RanksQuestID, Comp7QuestType.RANKS)
        self.__periodicQuests = self.__parseQuestsByDivision(comp7Quests, parseComp7PeriodicQuestID, Comp7QuestType.PERIODIC)

    def __setRanksData(self, model):
        itemsArray = model.getItems()
        itemsArray.clear()
        for rankIdx, _ in enumerate(self.ranksConfig.ranksOrder):
            itemModel = RankRewardsItemModel()
            self.__setRank(itemModel, rankIdx)
            itemsArray.addViewModel(itemModel)

        itemsArray.invalidate()

    def __setRank(self, itemModel, rankIdx):
        divisions = getRankDivisions(rankIdx, self.ranksConfig)
        division = first(divisions)
        setRankData(itemModel, self.viewModel, rankIdx, self.ranksConfig)
        setDivisionData(itemModel, divisions)
        self.__setRankRewards(itemModel, division)

    def __setRankRewards(self, itemModel, division):
        rankQuest = self.__rankQuests.get(division.dvsnID)
        periodicQuest = self.__periodicQuests.get(division.dvsnID)
        if rankQuest is None:
            _logger.error('Missing Competitive7x7 Rank Quests for division %s.', division)
            return
        else:
            rewardState = RankRewardsState.ACHIEVED if rankQuest.isCompleted() else RankRewardsState.NOTACHIEVED
            itemModel.setRewardsState(rewardState)
            bonuses, tooltips = packRanksRewardsQuestBonuses(rankQuest, periodicQuest)
            bonusData = zip(bonuses, tooltips)
            rank = comp7_shared.getRankEnumValue(division)
            self.__bonusData[rank] = []
            self.__bonusData[rank].extend(self.__setMainReward(itemModel, bonusData))
            self.__bonusData[rank].extend(self.__setRegularRewards(itemModel, bonusData))
            return

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

    @args2params(int, int)
    def __onPreviewOpen(self, rank, index):
        bonus = first(self.__bonusData[rank]).bonus
        style = self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, bonus.getStyleID())
        vehicleCD = self.__getPreviewVehicle(style)
        outfit = self.__getPreviewOutfit(style, bonus)
        showStylePreview(vehicleCD, style, backCallback=lambda : self.__backToRankRewardsScreenCallback(index), outfit=outfit)

    def __backToRankRewardsScreenCallback(self, index):
        hideVehiclePreview(back=False, close=True)
        shared_events.showComp7MetaRootView(self.pageId, index=index)

    @classmethod
    def __getPreviewVehicle(cls, style):
        if g_currentVehicle.isPresent() and style.mayInstall(g_currentVehicle.item):
            return g_currentVehicle.item.intCD
        accDossier = cls.__itemsCache.items.getAccountDossier()
        vehicles = accDossier.getComp7StatsS2().getVehicles()
        if not vehicles:
            vehicles = accDossier.getRandomStats().getVehicles()
        if vehicles:
            sortedVehicles = sorted(vehicles.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
            for vehicleCD, _ in sortedVehicles:
                vehicle = cls.__itemsCache.items.getVehicleCopyByCD(vehicleCD)
                if style.mayInstall(vehicle):
                    return vehicleCD

        else:
            getVehicles = cls.__itemsCache.items.getVehicles
            sortedVehicles = sorted(getVehicles(REQ_CRITERIA.INVENTORY).values(), key=lambda vehicle: vehicle.level, reverse=True)
            for vehicle in sortedVehicles:
                if style.mayInstall(vehicle):
                    return vehicle.intCD

        vehicleDescr = VehicleDescriptor(typeName=_DEFAULT_PREVIEW_VEHICLE_TYPE)
        return vehicleDescr.type.compactDescr

    @classmethod
    def __getPreviewOutfit(cls, style, bonus):
        branchID = bonus.getBranchID()
        progressLevel = bonus.getProgressLevel()
        camo = getComp7ProgressionStyleCamouflage(style.id, branchID, progressLevel)
        season = first(style.seasons)
        outfit = style.getOutfit(season)
        outfitComponent = outfit.pack()
        for camoComponent in outfitComponent.camouflages:
            camoComponent.id = camo.id

        outfitComponent = style.descriptor.addPartsToOutfit(season, outfitComponent, outfit.vehicleCD)
        return cls.__itemsFactory.createOutfit(component=outfitComponent, vehicleCD=outfit.vehicleCD)

    @staticmethod
    def __setMainReward(itemModel, bonusData):
        packedBonus, tooltip = bonusData.pop(0)
        packedBonus.setTooltipId(str(0))
        mainReward = itemModel.getMainReward()
        mainReward.clear()
        mainReward.addViewModel(packedBonus)
        mainReward.invalidate()
        return [_BonusData(packedBonus, tooltip)]

    @staticmethod
    def __setRegularRewards(itemModel, bonusData):
        packedBonusData = []
        rewards = itemModel.getRewards()
        rewards.clear()
        for idx, (packedBonus, tooltipData) in enumerate(bonusData):
            packedBonus.setTooltipId(str(idx + 1))
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
            if division.index == 0:
                result[division.dvsnID] = q

        return result
