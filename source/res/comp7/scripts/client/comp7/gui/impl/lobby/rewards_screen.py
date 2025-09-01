# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/rewards_screen.py
import logging
from collections import namedtuple
from copy import copy
import Windowing
import typing
from shared_utils import first, findFirst
import SoundGroups
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_LAST_SEASON_WITH_SEEN_REWARD, COMP7_LAST_MASKOT_WITH_SEEN_REWARD
from comp7.gui.game_control.comp7_shop_controller import ShopControllerStatus
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews, Rank
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.rewards_screen_model import Type, RewardsScreenModel, ShopInfoType, VideoState
from comp7.gui.impl.gen.view_models.views.lobby.season_result import SeasonResult
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared, comp7_qualification_helpers
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import packRanksRewardsQuestBonuses, packTokensRewardsQuestBonuses, packQualificationRewardsQuestBonuses, packYearlyRewardsBonuses, packYearlyRewardVehicleBonuses, packSelectedRewardsBonuses
from comp7.gui.impl.lobby.comp7_helpers.comp7_lobby_sounds import VehicleVideoSounds
from comp7.gui.impl.lobby.comp7_helpers.comp7_model_helpers import getYearlyRewardsRank
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import parseComp7RanksQuestID, getPeriodicQuestsByDivision
from comp7.gui.prb_control.entities import comp7_prb_helpers
from comp7.gui.selectable_reward.common import Comp7SelectableRewardManager
from comp7.gui.shared import event_dispatcher
from comp7.skeletons.gui.game_control import IComp7ShopController
from comp7_common_const import seasonPointsCodeBySeasonNumber, COMP7_MASKOT_ID
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import getSeasonNameEnum
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from frameworks.wulf.view.array import fillIntsArray, fillViewModelsArray
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import TooltipData
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.server_events.bonuses import VehiclesBonus
from gui.shared import event_dispatcher as shared_events
from gui.sounds.filters import switchVideoOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller, IHangarSpaceSwitchController
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Tuple, Callable
    from comp7_ranks_common import Comp7Division
    from frameworks.wulf import Command
    from frameworks.wulf.view.view_event import ViewEvent
    from gui.server_events.event_items import TokenQuest
_logger = logging.getLogger(__name__)
_MAX_MAIN_REWARDS_COUNT = 4
_MAIN_REWARDS = ('styleProgress', 'dossier_badge', 'dogTagComponents')
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))

class _BaseRewardsView(ViewImpl):
    __slots__ = ('_bonusData',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.comp7.mono.lobby.rewards_screen())
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
        elif contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView():
            vehicleCD = int(event.getArgument('vehicleCD'))
            return VehicleRolesTooltipView(vehicleCD)
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
    _comp7Controller = dependency.descriptor(IComp7Controller)
    _comp7ShopController = dependency.descriptor(IComp7ShopController)
    _spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    def _onLoading(self, *args, **kwargs):
        super(_QuestRewardsView, self)._onLoading(*args, **kwargs)
        if self._comp7ShopController.getProducts():
            self._setProductsData()

    def _setProductsData(self):
        raise NotImplementedError

    def _getEvents(self):
        return super(_QuestRewardsView, self)._getEvents() + ((self.viewModel.onOpenShop, self.__onOpenShop), (self._comp7ShopController.onDataUpdated, self.__onShopStatusUpdated))

    def __onShopStatusUpdated(self, status):
        if status == ShopControllerStatus.DATA_READY:
            self._setProductsData()

    def __onOpenShop(self):
        if not self._comp7Controller.isModePrbActive():
            self._spaceSwitchController.onSpaceUpdated += self.__onSpaceUpdated
            comp7_prb_helpers.selectComp7()
            return
        self.__goToShop()

    def __onSpaceUpdated(self):
        if not self._comp7Controller.isModePrbActive():
            return
        self._spaceSwitchController.onSpaceUpdated -= self.__onSpaceUpdated
        self.__goToShop()

    def __goToShop(self):
        event_dispatcher.showComp7MetaRootTab(tabId=MetaRootViews.SHOP)
        self.destroyWindow()


class RanksRewardsView(_QuestRewardsView):
    __slots__ = ('__division',)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, *args, **kwargs):
        super(RanksRewardsView, self).__init__(*args, **kwargs)
        quest = first(kwargs['quests'])
        self.__division = parseComp7RanksQuestID(quest.getID())

    def _onLoading(self, *args, **kwargs):
        super(RanksRewardsView, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as vm:
            rankValue = comp7_shared.getRankEnumValue(self.__division)
            divisionValue = comp7_shared.getDivisionEnumValue(self.__division)
            vm.setSeasonName(getSeasonNameEnum(self.__comp7Controller, SeasonName))
            vm.setType(self._getType())
            vm.setRank(rankValue)
            vm.setDivision(divisionValue)
            vm.setHasRankInactivity(comp7_shared.hasRankInactivity(self.__division.rank))

    def _packBonuses(self, *args, **kwargs):
        periodicQuestsByDivision = getPeriodicQuestsByDivision()
        periodicQuest = periodicQuestsByDivision.get(self.__division.dvsnID)
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
        ranksConfig = self.__comp7Controller.getRanksConfig()
        return Type.RANK if len(ranksConfig.divisionsByRank[self.__division.rank]) == self.__division.index else Type.DIVISION


class TokensRewardsView(_QuestRewardsView):

    def __init__(self, *args, **kwargs):
        super(TokensRewardsView, self).__init__(*args, **kwargs)
        self.__willOpenRewardsSelection = False

    def willOpenRewardsSelection(self):
        return self.__willOpenRewardsSelection

    def _onLoading(self, *args, **kwargs):
        super(TokensRewardsView, self)._onLoading(self, *args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setSeasonName(getSeasonNameEnum(self._comp7Controller, SeasonName))
            vm.setType(Type.TOKENSREWARDS)
            quest = first(kwargs['quests'])
            vm.setTokensCount(sum((token.getNeededCount() for token in quest.accountReqs.getTokens())))
            isSelectableReward = self.__isSelectableReward(quest)
            vm.setHasNextScreen(isSelectableReward)
        if isSelectableReward:
            AccountSettings.setNotifications(COMP7_LAST_SEASON_WITH_SEEN_REWARD, self._comp7Controller.getActualSeasonNumber())

    def _packBonuses(self, *args, **kwargs):
        return packTokensRewardsQuestBonuses(quest=first(kwargs['quests']))

    def _setProductsData(self):
        self.viewModel.setShopInfoType(ShopInfoType.NONE)

    def _getMainRewardsCount(self):
        return _MAX_MAIN_REWARDS_COUNT

    def _getEvents(self):
        return super(TokensRewardsView, self)._getEvents() + ((self.getViewModel().onOpenNextScreen, self.__onOpenNextScreen),)

    def _onClose(self):
        self.__willOpenRewardsSelection = False
        self.destroyWindow()

    def __onOpenNextScreen(self):
        self.__willOpenRewardsSelection = True
        self.destroyWindow()
        event_dispatcher.showComp7WeeklyQuestsRewardsSelectionWindow()

    def __isSelectableReward(self, quest):
        for bonus in quest.getBonuses():
            if bonus.getName() == SELECTABLE_BONUS_NAME:
                tokens = bonus.getTokens()
                if findFirst(Comp7SelectableRewardManager.isFeatureReward, tokens.iterkeys()) is not None:
                    return True

        return False


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
            vm.setSeasonName(getSeasonNameEnum(self._comp7Controller, SeasonName))
            vm.setType(Type.QUALIFICATIONRANK)
            vm.setRank(maxRankEnumValue)
            vm.setDivision(comp7_shared.getDivisionEnumValue(maxDivision))
            vm.setHasRankInactivity(comp7_shared.hasRankInactivity(maxDivision.rank))
            comp7_qualification_helpers.setQualificationBattles(vm.getQualificationBattles())
            fillIntsArray(rankEnumValues, vm.getRankList())

    def _packBonuses(self, *args, **kwargs):
        return packQualificationRewardsQuestBonuses(quests=kwargs['quests'])

    def _setProductsData(self):
        if self.__hasShopProduct() and self._comp7ShopController.isShopEnabled:
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
    __slots__ = ('__hasOfferReward', '__hasYearlyVehicle', '__bonuses', '__willOpenRewardsSelection')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __offersDataProvider = dependency.descriptor(IOffersDataProvider)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(YearlyRewardsView, self).__init__(*args, **kwargs)
        self.__bonuses = kwargs['bonuses']
        tokenBonus = self.__bonuses.get('tokens', {}).keys()
        self.__hasOfferReward = bool(findFirst(Comp7SelectableRewardManager.isFeatureReward, tokenBonus))
        self.__hasYearlyVehicle = VehiclesBonus.VEHICLES_BONUS in self.__bonuses
        self.__willOpenRewardsSelection = False

    def willOpenRewardsSelection(self):
        return self.__willOpenRewardsSelection

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
            vm.setType(Type.YEARLYREWARDS)
            vm.setHasYearlyVehicle(self.__hasYearlyVehicle)
            vm.setShowSeasonResults(showSeasonResults)
            if showSeasonResults:
                self.__updateSeasonsResults(vm)
            self.__updateYearlyVehicle(vm, self.__bonuses)
            vm.setHasNextScreen(self.__hasOfferReward)
            vm.setVideoState(VideoState.NOTSTARTED)
        if self.__hasOfferReward:
            AccountSettings.setNotifications(COMP7_LAST_MASKOT_WITH_SEEN_REWARD, COMP7_MASKOT_ID)

    def _finalize(self):
        self.__bonuses = None
        super(YearlyRewardsView, self)._finalize()
        return

    def _getEvents(self):
        return super(YearlyRewardsView, self)._getEvents() + ((self.getViewModel().onOpenNextScreen, self.__onOpenNextScreen),
         (self.getViewModel().onChangeType, self.__onChangeType),
         (self.getViewModel().onVideoStateChange, self.__onVideoStateChange),
         (self.__offersDataProvider.onOffersUpdated, self.__onOffersUpdated))

    def _packBonuses(self, *args, **kwargs):
        bonuses = copy(kwargs['bonuses'])
        if self.viewModel.getType() == Type.YEARLYVEHICLE:
            return packYearlyRewardVehicleBonuses(bonuses=bonuses)
        else:
            bonuses.pop('vehicles', None)
            return packYearlyRewardsBonuses(bonuses=bonuses)

    def _getMainRewardsCount(self):
        return 0 if self.viewModel.getType() == Type.YEARLYVEHICLE else _MAX_MAIN_REWARDS_COUNT

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
            seasonResult.setSeasonName(getSeasonNameEnum(self.__comp7Controller, SeasonName, season))
            seasonResult.setRank(comp7_shared.getRankEnumValue(division))
            results.append(seasonResult)

        fillViewModelsArray(results, model.getSeasonsResults())

    def __onWindowAccessibilityChanged(self, _):
        newVideoState = VideoState.RESUMED if Windowing.isWindowAccessible() else VideoState.PAUSED
        self.__onVideoStateChange({'state': newVideoState})

    def __updateYearlyVehicle(self, model, bonuses):
        if not self.__hasYearlyVehicle:
            return
        vehicles = first(bonuses[VehiclesBonus.VEHICLES_BONUS])
        vehicleCD = first(vehicles.keys())
        vehicleItem = self.__itemsCache.items.getItemByCD(vehicleCD)
        fillVehicleModel(model.vehicle, vehicleItem)
        if vehicleItem and vehicleItem.isInInventory:
            shared_events.selectVehicleInHangar(vehicleCD)

    def __onOffersUpdated(self):
        if not self.__hasOfferReward:
            return
        self._packBonusData(bonuses=self.__bonuses)
        self._setRewards()

    def __onOpenNextScreen(self):
        self.__willOpenRewardsSelection = self.__hasOfferReward
        self.destroyWindow()
        if self.__hasOfferReward:
            event_dispatcher.showComp7YearlyRewardsSelectionWindow()

    _onClose = __onOpenNextScreen

    @args2params(Type)
    def __onChangeType(self, newType):
        self.viewModel.setType(newType)
        if newType != Type.YEARLYVEHICLE:
            return
        else:
            rank = getYearlyRewardsRank()
            if rank is not None:
                self.viewModel.setRank(rank)
            self._packBonusData(bonuses=self.__bonuses)
            self._setRewards()
            return

    @args2params(VideoState)
    def __onVideoStateChange(self, state):
        self.viewModel.setVideoState(state)
        if state == VideoState.STARTED:
            Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
            switchVideoOverlaySoundFilter(on=True)
            SoundGroups.g_instance.playSound2D(VehicleVideoSounds.START)
        elif state == VideoState.PAUSED or state == VideoState.RESUMED:
            soundName = VehicleVideoSounds.RESUME if Windowing.isWindowAccessible() else VehicleVideoSounds.PAUSE
            SoundGroups.g_instance.playSound2D(soundName)
        elif state == VideoState.ENDED:
            Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
            SoundGroups.g_instance.playSound2D(VehicleVideoSounds.END)
            switchVideoOverlaySoundFilter(on=False)


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

    def __init__(self, quest, parent=None):
        super(RanksRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RanksRewardsView(quests=(quest,)), layer=WindowLayer.TOP_WINDOW, parent=parent)


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
