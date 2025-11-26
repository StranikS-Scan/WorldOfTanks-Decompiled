# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/meta_view/pages/yearly_rewards_page.py
from functools import partial
import typing
from shared_utils import first, findFirst
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews, Rank, SeasonPointState
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.yearly_rewards_card_model import YearlyRewardsCardModel, RewardsState
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.yearly_rewards_model import YearlyRewardsModel, BannerState
from comp7.gui.impl.gen.view_models.views.lobby.progression_item_base_model import ProgressionItemBaseModel
from comp7.gui.impl.gen.view_models.views.lobby.season_point_model import SeasonPointModel
from comp7.gui.impl.gen.view_models.views.lobby.year_model import YearState
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import packYearlyRewardMetaView
from comp7.gui.impl.lobby.comp7_helpers.comp7_c11n_helpers import getStylePreviewVehicle
from comp7.gui.impl.lobby.comp7_helpers.comp7_model_helpers import SEASONS_NUMBERS_BY_NAME
from comp7.gui.impl.lobby.comp7_helpers.comp7_model_helpers import setElitePercentage
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import hasAvailableOfferYearlyRewardGiftTokens, hasYearlyRewardToken
from comp7.gui.impl.lobby.comp7_helpers.comp7_shared import getPlayerDivisionByRating, getRankEnumValue, getPlayerDivision
from comp7.gui.impl.lobby.meta_view.meta_view_helper import getRankDivisions, setDivisionData, setRankData
from comp7.gui.impl.lobby.meta_view.pages import PageSubModelPresenter
from comp7.gui.impl.lobby.tooltips.crew_members_tooltip import CrewMembersTooltip
from comp7.gui.impl.lobby.tooltips.fifth_rank_tooltip import FifthRankTooltip
from comp7.gui.impl.lobby.tooltips.general_rank_tooltip import GeneralRankTooltip
from comp7.gui.impl.lobby.tooltips.season_point_tooltip import SeasonPointTooltip
from comp7.gui.impl.lobby.tooltips.sixth_rank_tooltip import SixthRankTooltip
from comp7.gui.impl.lobby.tooltips.style3d_tooltip import Style3dTooltip
from comp7.gui.shared.event_dispatcher import showComp7YearlyRewardsSelectionWindow, showComp7StylePreview, showComp7MetaRootTab
from comp7_common_const import seasonPointsCodeBySeasonNumber
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import getSeasonNameEnum
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_shared import getProgressionYearState
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from items.vehicles import makeVehicleTypeCompDescrByName
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
_DEFAULT_PREVIEW_VEHICLE = 'uk:GB91_Super_Conqueror'

class YearlyRewardsPage(PageSubModelPresenter):
    __slots__ = ('__tooltips', '__bonusData')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __c11nService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, viewModel, parentView):
        super(YearlyRewardsPage, self).__init__(viewModel, parentView)
        self.__tooltips = []
        self.__bonusData = {}

    @property
    def pageId(self):
        return MetaRootViews.YEARLYREWARDS

    @property
    def viewModel(self):
        return super(YearlyRewardsPage, self).getViewModel()

    @property
    def ranksConfig(self):
        return self.__comp7Controller.getRanksConfig()

    def initialize(self, **params):
        super(YearlyRewardsPage, self).initialize(**params)
        self.__updateAllData()

    def finalize(self):
        self.__tooltips = []
        self.__bonusData = {}
        super(YearlyRewardsPage, self).finalize()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltips[int(tooltipId)]
            if tooltipData:
                window = backport.BackportTooltipWindow(tooltipData, self.parentView.getParentWindow())
                window.load()
                return window
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7.mono.lobby.tooltips.season_point_tooltip():
            params = {'state': SeasonPointState(event.getArgument('state')),
             'ignoreState': event.getArgument('ignoreState')}
            return SeasonPointTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.general_rank_tooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.fifth_rank_tooltip():
            return FifthRankTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.sixth_rank_tooltip():
            return SixthRankTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.style3d_tooltip():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltips[int(tooltipId)]
            return Style3dTooltip(*tooltipData.specialArgs)
        elif contentID == R.views.comp7.mono.lobby.tooltips.crew_members_tooltip():
            return CrewMembersTooltip()
        elif contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView():
            vehicleCD = int(event.getArgument('vehicleCD'))
            return VehicleRolesTooltipView(vehicleCD)
        elif contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            fromIndex = int(event.getArgument('fromIndex'))
            index = int(event.getArgument('index'))
            bonuses = [ bonus for bonus in self.__bonusData[index][fromIndex - 1:] ]
            return AdditionalRewardsTooltip(bonuses)
        else:
            return

    def _getEvents(self):
        return ((self.viewModel.onGoToStylePreview, self.__onStylePreviewOpen),
         (self.viewModel.onGoToVehiclePreview, self.__onVehiclePreviewOpen),
         (self.viewModel.onGoToRewardsSelection, self.__onGoToRewardsSelection),
         (self.viewModel.onIntroViewed, self.__setInitialAnimationViewed),
         (self.__comp7Controller.onQualificationStateUpdated, self.__onQualificationStateUpdated),
         (self.__comp7Controller.onSeasonPointsUpdated, self.__onSeasonPointsUpdated),
         (self.__comp7Controller.onRankUpdated, self.__onRankUpdated),
         (self.__comp7Controller.onModeConfigChanged, self.__onConfigChanged),
         (self.__comp7Controller.onComp7RanksConfigChanged, self.__onRanksConfigChanged),
         (self.__comp7Controller.onComp7RewardsConfigChanged, self.__onRewardsConfigChanged),
         (self.__comp7Controller.onEntitlementsUpdated, self.__onEntitlementsUpdated),
         (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted))

    def __onQualificationStateUpdated(self):
        self.__updateAllData()

    def __onSeasonPointsUpdated(self):
        self.__updateAllData()

    def __onSeasonPointsReloaded(self, isSuccess):
        if isSuccess and self.isLoaded:
            self.__updateAllData()

    def __onRankUpdated(self, *_):
        self.__updateAllData()

    def __onConfigChanged(self):
        self.__updateAllData()

    def __onRanksConfigChanged(self):
        with self.viewModel.transaction() as tx:
            self.__setLegendData(tx)

    def __onRewardsConfigChanged(self):
        with self.viewModel.transaction() as tx:
            self.__setCards(tx)

    def __onEntitlementsUpdated(self):
        self.__updateAllData()

    @args2params(int)
    def __onStylePreviewOpen(self, cardIndex):
        bonuses = self.__bonusData[cardIndex]
        styleBonus = findFirst(lambda bonus: bonus.getName() == 'customizations', bonuses)
        self.__showStylePreview(styleBonus, cardIndex)

    @args2params(int, int)
    def __onVehiclePreviewOpen(self, cd, cardIndex):
        bonuses = self.__bonusData[cardIndex]
        styleBonus = findFirst(lambda bonus: bonus.getName() == 'styleProgressToken', bonuses)
        self.__showStylePreview(styleBonus, cardIndex, vehicleCD=cd)

    def __showStylePreview(self, styleBonus, cardIndex, vehicleCD=None):
        styleId = styleBonus.getStyleID() if styleBonus else None
        style = self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
        vehicleCD = getStylePreviewVehicle(style, makeVehicleTypeCompDescrByName(_DEFAULT_PREVIEW_VEHICLE)) if not vehicleCD else vehicleCD
        params = {'backCallback': partial(showComp7MetaRootTab, self.pageId, index=cardIndex)}
        showComp7StylePreview(vehicleCD, style, **params)
        return

    @args2params(str, int)
    def __onGoToRewardsSelection(self, name, cardIndex):
        showComp7YearlyRewardsSelectionWindow(category=name)

    def __setInitialAnimationViewed(self):
        with self.viewModel.transaction() as tx:
            tx.setWithIntro(False)
            self.__setYearlyAnimationSeen()

    def __onSyncCompleted(self, reason, *_):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            self.__updateAllData()

    def __updateAllData(self):
        with self.viewModel.transaction() as tx:
            self.__setCommonData(tx)
            self.__setCards(tx)

    def __setCommonData(self, model):
        receivedSeasonPoints = self.__comp7Controller.getReceivedSeasonPoints()
        model.setHasDataError(not receivedSeasonPoints)
        model.setWithIntro(not self.__isYearlyAnimationSeen())
        self.__setSeasonData(model)
        self.__setLegendData(model)

    def __areActualSeasonPointsReceived(self):
        actualSeason = self.__comp7Controller.getActualSeasonNumber(includePreannounced=True)
        if actualSeason is None:
            return False
        else:
            actualSeasonPointsEntitlement = seasonPointsCodeBySeasonNumber(actualSeason)
            return self.__comp7Controller.getReceivedSeasonPoints().get(actualSeasonPointsEntitlement, 0) > 0

    def __setSeasonData(self, model):
        actualSeason = self.__comp7Controller.getActualSeasonNumber(includePreannounced=True)
        if actualSeason is None:
            return
        else:
            currentSeason = self.__comp7Controller.getCurrentSeason()
            if currentSeason is not None:
                isQualificationActive = self.__comp7Controller.isQualificationActive()
            else:
                isQualificationActive = not self.__comp7Controller.isQualificationPassedInSeason(actualSeason)
            model.setIsQualificationActive(isQualificationActive)
            if not isQualificationActive:
                division = getPlayerDivisionByRating(self.__comp7Controller.getRatingForSeason(actualSeason))
                model.setCurrentRank(getRankEnumValue(division))
            seasons = self.__comp7Controller.getAllSeasons()
            canBeRewarded = any((self.__comp7Controller.isQualificationPassedInSeason(s.getNumber()) for s in seasons))
            yearState = getProgressionYearState(self.__comp7Controller, YearState)
            if yearState == YearState.FINISHED and canBeRewarded:
                if not hasYearlyRewardToken():
                    model.setBannerState(BannerState.NOTACCRUEDREWARDS)
                elif hasAvailableOfferYearlyRewardGiftTokens():
                    model.setBannerState(BannerState.REWARDSSELECTIONAVAILABLE)
                else:
                    model.setBannerState(BannerState.REWARDSRECEIVED)
            else:
                model.setBannerState(BannerState.DEFAULT)
            return

    def __setLegendData(self, model):
        ranksArray = model.getRanks()
        ranksArray.clear()
        for rank in self.ranksConfig.ranksOrder:
            rankModel = ProgressionItemBaseModel()
            setRankData(rankModel, rank, self.ranksConfig)
            setDivisionData(rankModel, getRankDivisions(rank, self.ranksConfig))
            ranksArray.addViewModel(rankModel)

        ranksArray.invalidate()
        setElitePercentage(model)

    def __setCards(self, model):
        cards = model.getCards()
        cards.clear()
        self.__tooltips = []
        self.__bonusData = {}
        prevRewardsCost = 0
        seasonPointsGenerator = _SeasonPointsGenerator(self.__areActualSeasonPointsReceived())
        sortedRewards = sorted(self.__comp7Controller.getYearlyRewards().main, key=lambda data: data['cost'])
        for idx, rewardsData in enumerate(sortedRewards):
            cardSeasonPoints = seasonPointsGenerator.getNext(rewardsData['cost'] - prevRewardsCost)
            prevRewardsCost = rewardsData['cost']
            cardModel = YearlyRewardsCardModel()
            cardModel.setRewardsState(self.__getRewardStateForCard(cardSeasonPoints))
            self.__setCardSeasonPoints(cardModel, cardSeasonPoints)
            self.__bonusData[idx] = self.__fillRewards(cardModel, rewardsData['bonus'])
            cards.addViewModel(cardModel)

        cards.invalidate()

    def __getRewardStateForCard(self, cardSeasonPoints):
        if all((pointState == SeasonPointState.ACHIEVED for pointState, _ in cardSeasonPoints)):
            if hasYearlyRewardToken():
                return RewardsState.CLAIMED
            return RewardsState.GUARANTEED
        return RewardsState.POSSIBLE if not any((pointState == SeasonPointState.NOTACHIEVED for pointState, _ in cardSeasonPoints)) else RewardsState.NOTAVAILABLE

    def __fillRewards(self, cardModel, bonuses):
        rewards = cardModel.getRewards()
        rewards.clear()
        bonusModels, tooltipsData = packYearlyRewardMetaView(bonuses)
        for idx, bonusModel in enumerate(bonusModels):
            bonusModel.setTooltipId(str(len(self.__tooltips)))
            rewards.addViewModel(bonusModel)
            self.__tooltips.append(tooltipsData[idx])

        rewards.invalidate()
        self.__setCardVehicleData(cardModel, bonuses)
        return bonusModels

    @staticmethod
    def __setCardSeasonPoints(cardModel, cardSeasonPoints):
        pointsList = cardModel.getSeasonPoints()
        pointsList.clear()
        for state, season in cardSeasonPoints:
            pointModel = SeasonPointModel()
            pointModel.setState(state)
            if season is not None:
                pointModel.setSeason(season)
            pointsList.addViewModel(pointModel)

        pointsList.invalidate()
        return

    def __setCardVehicleData(self, model, bonuses):
        vehicleBonus = bonuses.get('vehicles')
        if vehicleBonus is not None:
            vehicleItem = self.__itemsCache.items.getItemByCD(first(vehicleBonus.keys()))
            fillVehicleModel(model.vehicle, vehicleItem)
        return

    def __setYearlyAnimationSeen(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags[GuiSettingsBehavior.COMP7_YEARLY_ANIMATION_SEEN] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)

    def __isYearlyAnimationSeen(self):
        section = self.__settingsCore.serverSettings.getSection(section=GUI_START_BEHAVIOR, defaults=AccountSettings.getFilterDefault(GUI_START_BEHAVIOR))
        return section.get(GuiSettingsBehavior.COMP7_YEARLY_ANIMATION_SEEN)


class _SeasonPointsGenerator(object):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, areActualSeasonPointsReceived):
        self.__allPointsStates = self.__composePointsStates(areActualSeasonPointsReceived)

    def getNext(self, rewardsCount):
        result, self.__allPointsStates = self.__allPointsStates[:rewardsCount], self.__allPointsStates[rewardsCount:]
        if len(result) < rewardsCount:
            result += [(SeasonPointState.NOTACHIEVED, None)] * (rewardsCount - len(result))
        return result

    def __composePointsStates(self, areActualSeasonPointsReceived):
        result = []
        achievedPoints = self.__getAchievedPoints()
        for seasonName, count in achievedPoints:
            result += [(SeasonPointState.ACHIEVED, seasonName)] * count

        if self.__comp7Controller.getActualSeasonNumber(includePreannounced=True) is None:
            return result
        else:
            if not self.__comp7Controller.isQualificationActive() and not areActualSeasonPointsReceived:
                possiblePointsCount = getPlayerDivision().seasonPoints
                season = getSeasonNameEnum(self.__comp7Controller, SeasonName)
                result += [(SeasonPointState.POSSIBLE, season)] * possiblePointsCount
            return result

    def __getAchievedPoints(self):
        achievedPoints = []
        entitlementsCount = self.__comp7Controller.getReceivedSeasonPoints()
        orderedSeasons = sorted(SEASONS_NUMBERS_BY_NAME.items(), key=lambda x: x[1])
        for seasonName, seasonNumber in orderedSeasons:
            count = entitlementsCount.get(seasonPointsCodeBySeasonNumber(seasonNumber), 0)
            achievedPoints.append((SeasonName(seasonName), count))

        return achievedPoints
