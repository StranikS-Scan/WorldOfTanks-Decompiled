# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/rewards_screen.py
from collections import namedtuple
from copy import copy
import typing
from shared_utils import first, findFirst
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_YEARLY_REWARD_SEEN
from comp7_common import seasonPointsCodeBySeasonNumber
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from frameworks.wulf.view.array import fillIntsArray, fillViewModelsArray
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.game_control.comp7_shop_controller import ShopControllerStatus
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.gen.view_models.views.lobby.comp7.rewards_screen_model import Type, Rank, RewardsScreenModel, ShopInfoType
from gui.impl.gen.view_models.views.lobby.comp7.season_result import SeasonResult
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7 import comp7_shared, comp7_qualification_helpers
from gui.impl.lobby.comp7.comp7_bonus_packer import packRanksRewardsQuestBonuses, packTokensRewardsQuestBonuses, packQualificationRewardsQuestBonuses, packYearlyRewardsBonuses, packYearlyRewardCrew, packSelectedRewardsBonuses
from gui.impl.lobby.comp7.comp7_model_helpers import getSeasonNameEnum
from gui.impl.lobby.comp7.comp7_quest_helpers import parseComp7RanksQuestID, getRequiredTokensCountToComplete, parseComp7PeriodicQuestID
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prb_control.entities.comp7 import comp7_prb_helpers
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.event_dispatcher import showComp7MetaRootView, showComp7YearlyRewardsSelectionWindow
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller, IComp7ShopController, IHangarSpaceSwitchController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from frameworks.wulf.view.view_event import ViewEvent
    from gui.server_events.event_items import TokenQuest
_MAX_MAIN_REWARDS_COUNT = 4
_MAIN_REWARDS = ('styleProgress', 'dossier_badge', 'dogTagComponents')
_YEARLY_MAIN_REWARDS = ('dossier_badge', 'dossier_achievement', 'styleProgress', 'deluxe_gift', 'crystal')
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))

class _BaseRewardsView(ViewImpl):
    __slots__ = ('_bonusData',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.comp7.RewardsScreen())
        settings.model = RewardsScreenModel()
        settings.args = args
        settings.kwargs = kwargs
        super(_BaseRewardsView, self).__init__(settings)
        self._bonusData = []

    @property
    def viewModel(self):
        return super(_BaseRewardsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is not None:
                bonusData = self._bonusData[int(tooltipId)]
                window = BackportTooltipWindow(bonusData.tooltip, self.getParentWindow(), event)
                window.load()
                return window
        return super(_BaseRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showCount'))
            showCount += self._getMainRewardsCount()
            bonuses = [ d.bonus for d in self._bonusData[showCount:] ]
            return AdditionalRewardsTooltip(bonuses)
        else:
            return None

    def _finalize(self):
        self._bonusData = None
        super(_BaseRewardsView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(_BaseRewardsView, self)._onLoading(*args, **kwargs)
        self._packBonusData(*args, **kwargs)
        self._setRewards()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose),)

    def _packBonuses(self, *args, **kwargs):
        raise NotImplementedError

    def _getMainRewardsCount(self):
        bonuses = [ d.bonus for d in self._bonusData ]
        mainRewards = [ bonusModel for bonusModel in bonuses if bonusModel.getName() in _MAIN_REWARDS ]
        return min(len(mainRewards), _MAX_MAIN_REWARDS_COUNT)

    def _onClose(self):
        self.destroyWindow()

    def _setRewards(self):
        mainRewardsCount = self._getMainRewardsCount()
        bonuses = [ d.bonus for d in self._bonusData ]
        fillViewModelsArray(bonuses[:mainRewardsCount], self.viewModel.getMainRewards())
        fillViewModelsArray(bonuses[mainRewardsCount:], self.viewModel.getAdditionalRewards())

    def _packBonusData(self, *args, **kwargs):
        self._bonusData = []
        bonuses, tooltips = self._packBonuses(*args, **kwargs)
        for idx, (packedBonus, tooltipData) in enumerate(zip(bonuses, tooltips)):
            packedBonus.setTooltipId(str(idx))
            self._bonusData.append(_BonusData(packedBonus, tooltipData))


class _QuestRewardsView(_BaseRewardsView):
    _comp7ShopController = dependency.descriptor(IComp7ShopController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    def _onLoading(self, *args, **kwargs):
        super(_QuestRewardsView, self)._onLoading(*args, **kwargs)
        if self._comp7ShopController.getProducts():
            self._setProductsData()

    def _setProductsData(self):
        raise NotImplementedError

    def _getEvents(self):
        eventList = list(super(_QuestRewardsView, self)._getEvents())
        eventList.extend(((self.viewModel.onOpenShop, self.__onOpenShop), (self._comp7ShopController.onDataUpdated, self.__onShopStatusUpdated)))
        return eventList

    def __onShopStatusUpdated(self, status):
        if status == ShopControllerStatus.DATA_READY:
            self._setProductsData()

    def __onOpenShop(self):
        if not self.__comp7Controller.isComp7PrbActive():
            self.__spaceSwitchController.onSpaceUpdated += self.__onSpaceUpdated
            comp7_prb_helpers.selectComp7()
            return
        self.__goToShop()

    def __onSpaceUpdated(self):
        if not self.__comp7Controller.isComp7PrbActive():
            return
        self.__spaceSwitchController.onSpaceUpdated -= self.__onSpaceUpdated
        self.__goToShop()

    def __goToShop(self):
        showComp7MetaRootView(tabId=MetaRootViews.SHOP)
        self.destroyWindow()


class RanksRewardsView(_QuestRewardsView):
    __slots__ = ('__division',)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        super(RanksRewardsView, self).__init__(*args, **kwargs)
        quest = first(kwargs['quests'])
        self.__division = parseComp7RanksQuestID(quest.getID())

    def _onLoading(self, *args, **kwargs):
        super(RanksRewardsView, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as vm:
            rankValue = comp7_shared.getRankEnumValue(self.__division)
            divisionValue = comp7_shared.getDivisionEnumValue(self.__division)
            vm.setSeasonName(getSeasonNameEnum())
            vm.setType(self._getType())
            vm.setRank(rankValue)
            vm.setDivision(divisionValue)
            vm.setHasRankInactivity(comp7_shared.hasRankInactivity(self.__division.rank))

    def _packBonuses(self, *args, **kwargs):
        periodicQuest = findFirst(lambda q: parseComp7PeriodicQuestID(q.getID()) == self.__division, kwargs.get('periodicQuests', []))
        return packRanksRewardsQuestBonuses(quest=first(kwargs['quests']), periodicQuest=periodicQuest)

    def _setProductsData(self):
        if self._getType() == Type.RANK:
            rank = comp7_shared.getRankEnumValue(self.__division)
            if self._comp7ShopController.hasNewProducts(rank):
                self.viewModel.setShopInfoType(ShopInfoType.OPEN)
            elif self._comp7ShopController.hasNewDiscounts(rank):
                self.viewModel.setShopInfoType(ShopInfoType.DISCOUNT)
            else:
                self.viewModel.setShopInfoType(ShopInfoType.NONE)
        else:
            self.viewModel.setShopInfoType(ShopInfoType.NONE)

    def _onClose(self):
        if self.viewModel.getType() == Type.RANK:
            self.viewModel.setType(Type.RANKREWARDS)
        else:
            self.destroyWindow()

    def _getType(self):
        ranksConfig = self.__lobbyCtx.getServerSettings().comp7RanksConfig
        return Type.RANK if len(ranksConfig.divisionsByRank[self.__division.rank]) == self.__division.index else Type.DIVISION


class TokensRewardsView(_QuestRewardsView):

    def _onLoading(self, *args, **kwargs):
        super(TokensRewardsView, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setSeasonName(getSeasonNameEnum())
            vm.setType(Type.TOKENSREWARDS)
            quest = first(kwargs['quests'])
            vm.setTokensCount(getRequiredTokensCountToComplete(quest.getID()))

    def _packBonuses(self, *args, **kwargs):
        return packTokensRewardsQuestBonuses(quest=first(kwargs['quests']))

    def _setProductsData(self):
        self.viewModel.setShopInfoType(ShopInfoType.NONE)

    def _getMainRewardsCount(self):
        return _MAX_MAIN_REWARDS_COUNT


class QualificationRewardsView(_QuestRewardsView):
    __slots__ = ('__divisions',)

    def __init__(self, *args, **kwargs):
        super(QualificationRewardsView, self).__init__(*args, **kwargs)
        self.__divisions = self.__getDivisions(kwargs['quests'])

    def _onLoading(self, *args, **kwargs):
        super(QualificationRewardsView, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as vm:
            maxDivision = first(self.__divisions)
            rankEnumValues = self.__getRanks(self.__divisions)
            maxRankEnumValue = first(rankEnumValues)
            vm.setSeasonName(getSeasonNameEnum())
            vm.setType(Type.QUALIFICATIONRANK)
            vm.setRank(maxRankEnumValue)
            vm.setDivision(comp7_shared.getDivisionEnumValue(maxDivision))
            vm.setHasRankInactivity(comp7_shared.hasRankInactivity(maxDivision.rank))
            comp7_qualification_helpers.setQualificationBattles(vm.getQualificationBattles())
            fillIntsArray(rankEnumValues, vm.getRankList())

    def _packBonuses(self, *args, **kwargs):
        return packQualificationRewardsQuestBonuses(quests=kwargs['quests'])

    def _setProductsData(self):
        if self.__hasShopProduct():
            self.viewModel.setShopInfoType(ShopInfoType.OPEN)
        else:
            self.viewModel.setShopInfoType(ShopInfoType.NONE)

    def _onClose(self):
        if self.viewModel.getType() == Type.QUALIFICATIONRANK:
            self.viewModel.setType(Type.QUALIFICATIONREWARDS)
        else:
            self.destroyWindow()

    def __getRanks(self, divisions):
        uniqueRanks = {comp7_shared.getRankEnumValue(division) for division in divisions}
        return sorted(list(uniqueRanks))

    def __getDivisions(self, quests):
        divisions = [ parseComp7RanksQuestID(quest.getID()) for quest in quests ]
        return sorted(divisions, key=lambda d: d.dvsnID)

    def __hasShopProduct(self):
        ranks = {comp7_shared.getRankEnumValue(division) for division in self.__divisions}
        for rank in ranks:
            if self._comp7ShopController.hasNewProducts(rank):
                return True

        return False


class YearlyRewardsView(_BaseRewardsView):
    __slots__ = ('__hasOfferReward', '__hasYearlyVehicle', '__bonuses')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __offersDataProvider = dependency.descriptor(IOffersDataProvider)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(YearlyRewardsView, self).__init__(*args, **kwargs)
        self.__bonuses = kwargs['bonuses']
        tokenBonus = self.__bonuses.get('tokens', {}).keys()
        self.__hasOfferReward = bool(findFirst(self.__comp7Controller.isComp7OfferToken, tokenBonus))
        self.__hasYearlyVehicle = VehiclesBonus.VEHICLES_BONUS in self.__bonuses

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId == TOOLTIPS_CONSTANTS.SHOP_VEHICLE:
                vehicleCD = int(event.getArgument('vehicleCD'))
                data = TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=[vehicleCD])
                window = BackportTooltipWindow(data, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
        return super(YearlyRewardsView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(YearlyRewardsView, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as vm:
            showSeasonResults = kwargs['showSeasonResults']
            vm.setType(Type.YEARLYVEHICLE if self.__hasYearlyVehicle else Type.YEARLYREWARDS)
            vm.setHasYearlyVehicle(self.__hasYearlyVehicle)
            vm.setShowSeasonResults(showSeasonResults)
            if showSeasonResults:
                self.__updateSeasonsResults(vm)
            self.__updateYearlyVehicle(vm, self.__bonuses)
        AccountSettings.setNotifications(COMP7_YEARLY_REWARD_SEEN, True)

    def _finalize(self):
        self.__bonuses = None
        super(YearlyRewardsView, self)._finalize()
        return

    def _getEvents(self):
        eventList = list(super(YearlyRewardsView, self)._getEvents())
        eventList.append((self.__offersDataProvider.onOffersUpdated, self.__onOffersUpdated))
        return eventList

    def _packBonuses(self, *args, **kwargs):
        bonuses = copy(kwargs['bonuses'])
        vehicleBonus = bonuses.pop('vehicles', None)
        return packYearlyRewardCrew(bonus=vehicleBonus) if self.__hasYearlyVehicle else packYearlyRewardsBonuses(bonuses=bonuses)

    def _getMainRewardsCount(self):
        bonuses = [ d.bonus for d in self._bonusData ]
        mainRewards = [ bonusModel for bonusModel in bonuses if bonusModel.getName() in _YEARLY_MAIN_REWARDS ]
        return min(len(mainRewards), _MAX_MAIN_REWARDS_COUNT)

    def _onClose(self):
        if self.viewModel.getType() == Type.YEARLYVEHICLE:
            self.__hasYearlyVehicle = False
            self.viewModel.setType(Type.YEARLYREWARDS)
            self._packBonusData(bonuses=self.__bonuses)
            self._setRewards()
            return
        super(YearlyRewardsView, self)._onClose()
        if self.__hasOfferReward:
            showComp7YearlyRewardsSelectionWindow()

    def __updateSeasonsResults(self, model):
        results = []
        for season in self.__comp7Controller.getAllSeasons():
            seasonNumber = season.getNumber()
            receivedSeasonPoints = self.__comp7Controller.getReceivedSeasonPoints()
            pointsCountInSeason = receivedSeasonPoints.get(seasonPointsCodeBySeasonNumber(seasonNumber), 0)
            rating = self.__comp7Controller.getRatingForSeason(seasonNumber)
            division = comp7_shared.getPlayerDivisionByRating(rating, seasonNumber)
            seasonResult = SeasonResult()
            seasonResult.setSeasonPointsCount(pointsCountInSeason)
            seasonResult.setSeasonName(getSeasonNameEnum(season))
            seasonResult.setRank(comp7_shared.getRankEnumValue(division))
            results.append(seasonResult)

        fillViewModelsArray(results, model.getSeasonsResults())

    def __updateYearlyVehicle(self, model, bonuses):
        if not self.__hasYearlyVehicle:
            return
        vehicles = first(bonuses[VehiclesBonus.VEHICLES_BONUS])
        vehicleCD = first(vehicles.keys())
        vehicleItem = self.__itemsCache.items.getItemByCD(vehicleCD)
        fillVehicleModel(model.vehicle, vehicleItem)

    def __onOffersUpdated(self):
        if not self.__hasOfferReward:
            return
        self._packBonusData(bonuses=self.__bonuses)
        self._setRewards()


class SelectedRewardsView(_BaseRewardsView):

    def _onLoading(self, *args, **kwargs):
        super(SelectedRewardsView, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setType(Type.SELECTEDREWARDS)

    def _packBonuses(self, *args, **kwargs):
        return packSelectedRewardsBonuses(bonuses=kwargs['bonuses'])

    def _getMainRewardsCount(self):
        return _MAX_MAIN_REWARDS_COUNT


class RanksRewardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, quest, periodicQuests, parent=None):
        super(RanksRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RanksRewardsView(quests=(quest,), periodicQuests=periodicQuests), layer=WindowLayer.TOP_WINDOW, parent=parent)


class TokensRewardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, quest, parent=None):
        super(TokensRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TokensRewardsView(quests=(quest,)), layer=WindowLayer.TOP_WINDOW, parent=parent)


class QualificationRewardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, quests, parent=None):
        super(QualificationRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=QualificationRewardsView(quests=quests), layer=WindowLayer.TOP_WINDOW, parent=parent)


class YearlyRewardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, bonuses, showSeasonResults, parent=None):
        super(YearlyRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=YearlyRewardsView(bonuses=bonuses, showSeasonResults=showSeasonResults), layer=WindowLayer.TOP_WINDOW, parent=parent)


class SelectedRewardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, bonuses, parent=None):
        super(SelectedRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SelectedRewardsView(bonuses=bonuses), layer=WindowLayer.TOP_WINDOW, parent=parent)
