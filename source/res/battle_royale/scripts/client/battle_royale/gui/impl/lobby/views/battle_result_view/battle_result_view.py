# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/battle_result_view/battle_result_view.py
import typing
from collections import OrderedDict
import SoundGroups
from arena_bonus_type_caps import ARENA_BONUS_TYPE
from battle_royale.gui.impl.lobby.tooltips.reward_currency_tooltip_view import RewardCurrencyTooltipView
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.battle_result_view_model import BattleResultViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.tooltip_constants_model import TooltipConstantsModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.stat_item_model import StatItemModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.leaderboard_constants import LeaderboardConstants
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.battle_reward_item_model import BattleRewardItemModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.place_model import PlaceModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.row_model import RowModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.battle_pass_progress import BattlePassProgress
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.shared import event_dispatcher, EVENT_BUS_SCOPE
from gui.shared.events import BattleRoyalePlatoonEvent
from gui.shared.lock_overlays import lockNotificationManager
from gui.server_events.battle_royale_formatters import BRSections
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattleRoyaleController, IBattlePassController, IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import first
from soft_exception import SoftException
from gui.sounds.ambients import BattleResultsEnv
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents
from battle_royale.gui.constants import BattleRoyaleSubMode
from gui.server_events import events_dispatcher
from gui.impl.backport.backport_context_menu import BackportContextMenuWindow
from gui.impl.backport.backport_context_menu import createContextMenuData
from battle_royale.gui.impl.lobby.views.battle_result_view import BATTLE_ROYALE_LOCK_SOURCE_NAME
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from skeletons.connection_mgr import IConnectionManager
from battle_pass_common import getPresentLevel
from messenger.storage import storage_getter
from messenger.formatters.service_channel_helpers import parseTokenBonusCount
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.impl.gen.view_models.views.battle_royale.battle_results.player_battle_type_status_model import BattleType
from gui.prb_control.entities.base.listener import IPrbListener
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.battle_royale.battle_results.player_battle_type_status_model import PlayerBattleTypeStatusModel
    from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_result_view.leaderboard_model import LeaderboardModel
_THE_BEST_PLACE = 1
_BR_POINTS_ICON = R.images.gui.maps.icons.battleRoyale.battleResult.leaderboard.br_selector_16()
_BATTLE_REWARD_TYPES = [BattleRewardItemModel.XP,
 BattleRewardItemModel.CREDITS,
 BattleRewardItemModel.BATTLE_PASS_POINTS,
 BattleRewardItemModel.CRYSTALS,
 BattleRewardItemModel.BATTLE_ROYALE_COIN,
 BattleRewardItemModel.BR_PROGRESSION_TOKEN]
_HIDDEN_BONUSES_WITH_ZERO_VALUES = frozenset([BattleRewardItemModel.CRYSTALS, BattleRewardItemModel.BATTLE_PASS_POINTS])
_TOURNAMENT_ARENA_BONUS_TYPES = (ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SQUAD)
_INVALID_PREBATTLE_ID = 0

class BrBattleResultsViewInLobby(ViewImpl, LobbyHeaderVisibility, IPrbListener):
    __slots__ = ('__arenaUniqueID', '__tooltipsData', '__tooltipParametersCreator', '__data', '__isObserverResult', '__arenaBonusType', '__ally', '__squadCreatedByInvite')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __brController = dependency.descriptor(IBattleRoyaleController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __brProgressionController = dependency.descriptor(IBRProgressionOnTokensController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __sound_env__ = BattleResultsEnv

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.battle_royale.lobby.views.BattleResultView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = BattleResultViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BrBattleResultsViewInLobby, self).__init__(settings)
        self.__arenaUniqueID = kwargs.get('ctx', {}).get('arenaUniqueID')
        if self.__arenaUniqueID is None:
            raise SoftException('There is not arenaUniqueID in battleResults context')
        self.__data = self.__battleResults.getResultsVO(self.__arenaUniqueID)
        if not self.__data:
            raise SoftException('There is not battleResults')
        commonData = self.__data.get(BRSections.COMMON)
        if commonData is None:
            raise SoftException('There is no common info in battle results')
        vehicleInfo = first(commonData.get('playerVehicles', []))
        self.__isObserverResult = vehicleInfo.get('isObserver', False) if vehicleInfo else False
        self.__arenaBonusType = self.__data[BRSections.COMMON].get('arenaBonusType', 0)
        self.__tooltipsData = {}
        self.__tooltipParametersCreator = self.__getTooltipParametersCreator()
        self.__ally = {}
        self.__squadCreatedByInvite = False
        return

    @property
    def viewModel(self):
        return super(BrBattleResultsViewInLobby, self).getViewModel()

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.battle_royale.lobby.tooltips.RewardCurrencyTooltipView():
            currencyType = event.getArgument('currencyType')
            return RewardCurrencyTooltipView(currencyType)
        return super(BrBattleResultsViewInLobby, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipID = self.__normalizeTooltipID(event.getArgument('tooltipId', ''))
            parametersCreator = self.__tooltipParametersCreator.get(tooltipID)
            if parametersCreator is None:
                raise SoftException('Invalid arguments to create an old flash tooltip with id {}'.format(tooltipID))
            tooltipParameters = parametersCreator(event)
            window = BackportTooltipWindow(tooltipParameters, self.getParentWindow())
            window.load()
            return window
        else:
            return super(BrBattleResultsViewInLobby, self).createToolTip(event)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuArgs = {}
            contextMenuArgs['databaseID'] = event.getArgument('databaseID')
            if self.__connectionMgr.databaseID == contextMenuArgs['databaseID']:
                return super(BrBattleResultsViewInLobby, self).createContextMenu(event)
            hiddenUserName = event.getArgument('hiddenUserName')
            contextMenuArgs['userName'] = hiddenUserName if hiddenUserName else event.getArgument('userName')
            contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BR_BATTLE_RESULT_CONTEXT_MENU, contextMenuArgs)
            currentPlayer = self.usersStorage.getUser(self.__connectionMgr.databaseID)
            isCurrentPlayer = currentPlayer.getName() == contextMenuArgs['userName']
            if contextMenuData is not None and not isCurrentPlayer:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(BrBattleResultsViewInLobby, self).createContextMenu(event)

    def _initialize(self, *args, **kwargs):
        super(BrBattleResultsViewInLobby, self)._initialize(*args, **kwargs)
        BREvents.playSound(BREvents.BATTLE_SUMMARY_SHOW)
        self.suspendLobbyHeader(self.uniqueID)
        event_dispatcher.hideSquadWindow()

    def _finalize(self):
        lockNotificationManager(False, source=BATTLE_ROYALE_LOCK_SOURCE_NAME)
        BREvents.playSound(BREvents.BR_RESULT_PROGRESS_BAR_STOP)
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.bp_progress_bar_stop()))
        self.__tooltipsData = None
        self.__tooltipParametersCreator = None
        self.__data = None
        self.__ally = None
        self.__squadCreatedByInvite = False
        self.resumeLobbyHeader(self.uniqueID)
        super(BrBattleResultsViewInLobby, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(BrBattleResultsViewInLobby, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__setPlayerBattleTypeStatus(model.playerBattleTypeStatus)
            self.__setPersonalResult(model.personalResults)
            self.__setLeaderboard(model.leaderboardLobbyModel)

    def _getEvents(self):
        return ((self.viewModel.personalResults.battlePassProgress.onSubmitClick, self.__onBattlePassClick),
         (self.viewModel.playerBattleTypeStatus.onInviteToPlatoon, self.__onInviteToPlatoonClick),
         (self.__brController.onUpdated, self.__updateBattlePass),
         (self.__platoonCtrl.onMembersUpdate, self.__updateSquadState))

    def _getListeners(self):
        return ((BattleRoyalePlatoonEvent.LEAVED_PLATOON, self.__onLeavedPlatoon, EVENT_BUS_SCOPE.LOBBY),)

    @storage_getter('users')
    def usersStorage(self):
        return None

    def __onBattlePassClick(self):
        self.destroyWindow()
        events_dispatcher.showMissionsBattlePass()

    def __updateBattlePass(self):
        self.__setBattlePass(self.viewModel.personalResults.battlePassProgress)
        self.__setBattleRewards(self.viewModel.personalResults)
        self.__setBattleRewardsWithPremium(self.viewModel.personalResults)

    def __updateSquadState(self):
        if not self.__squadCreatedByInvite or not self.__isCommander():
            if self.__brController.isInBattleRoyaleSquad():
                if all([ slot.get('player') is not None for slot in self.__platoonCtrl.getPlatoonSlotsData() ]):
                    self.__setIsPlatoonWindowOpen(True)
                    return
            self.__setIsPlatoonWindowOpen(False)
        return

    def __onInviteToPlatoonClick(self):
        self.__brController.selectSubModeBattle(BattleRoyaleSubMode.SQUAD_MODE_ID, accountsToInvite=(self.__ally.get('databaseID', 0),))
        self.__squadCreatedByInvite = True
        self.__setIsPlatoonWindowOpen(True)

    def __onLeavedPlatoon(self, *_):
        if self.__squadCreatedByInvite or not self.__isCommander():
            self.__squadCreatedByInvite = False
            self.__setIsPlatoonWindowOpen(False)

    def __setPlayerBattleTypeStatus(self, statusModel):
        commonInfo = self.__data.get(BRSections.COMMON)
        if commonInfo is None:
            raise SoftException('There is no vehicle status info in battle results')
        leaderboard = self.__data.get(BRSections.LEADERBOARD)
        if leaderboard is None:
            raise SoftException("There is no players' table in battle results")
        if self.__isSquadMode():
            for vehicle in leaderboard:
                if vehicle['place'] == commonInfo['playerPlace'] and not vehicle['isPersonal']:
                    self.__ally = vehicle
                    break

            self.__setUserName(statusModel.user, self.__ally)
            statusModel.setBattleType(BattleType.PLATOON if self.__ally.get('prebattleID', 0) != _INVALID_PREBATTLE_ID or self.__isTournament() else BattleType.RANDOMPLATOON)
        else:
            statusModel.setBattleType(BattleType.SOLO)
        self.__updateSquadState()
        return

    def __setPersonalResult(self, personalModel):
        self.__setMapName()
        self.__setCommonInfo()
        if not self.__isObserverResult:
            self.__setFinishResult(personalModel)
            self.__setStats(personalModel)
            self.__setBattleRewards(personalModel)
            self.__setBattleRewardsWithPremium(personalModel)
            self.__setCompletedQuests(personalModel)
        self.__setBattlePass(personalModel.battlePassProgress)

    def __setBattlePass(self, battlePassModel):
        battlePassData = self.__data[BRSections.PERSONAL][BRSections.BATTLE_PASS]
        chapterID = battlePassData['chapterID']
        currentLevelPoints = battlePassData['currentLevelPoints']
        totalPoints = self.__getBattlePassPointsTotal()
        battlePassModel.setEarnedPoints(min(totalPoints, currentLevelPoints))
        battlePassModel.setCurrentLevel(getPresentLevel(battlePassData['currentLevel']))
        battlePassModel.setMaxPoints(battlePassData['maxPoints'])
        battlePassModel.setCurrentLevelPoints(currentLevelPoints)
        isMaxLevel = self.__battlePassController.getMaxLevelInChapter(chapterID) == battlePassData['currentLevel']
        if isMaxLevel and battlePassData['isDone']:
            chapterID = 0
            currentLevelPoints = battlePassData['pointsAux']
            chapterState = ChapterState.COMPLETED
        else:
            chapterState = ChapterState.ACTIVE
            if currentLevelPoints == 0:
                currentLevelPoints = battlePassData['pointsTotal']
        battlePassModel.setChapterState(chapterState)
        battlePassModel.setChapterID(chapterID)
        state = BattlePassProgress.BP_STATE_DISABLED
        bpController = self.__battlePassController
        hasExtra = bpController.hasExtra()
        seasonNum = bpController.getSeasonNum()
        isBought = all((bpController.isBought(chapterID=chapter) for chapter in bpController.getChapterIDs()))
        if self.__brController.isBattlePassAvailable(self.__arenaBonusType) and not self.__isObserverResult:
            state = BattlePassProgress.BP_STATE_BOUGHT if isBought else BattlePassProgress.BP_STATE_NORMAL
        if battlePassData['battlePassComplete']:
            battlePassModel.setFreePoints(battlePassData['availablePoints'])
            battlePassModel.setProgressionState(BattlePassProgress.PROGRESSION_COMPLETED)
        else:
            battlePassModel.setFreePoints(currentLevelPoints)
            battlePassModel.setProgressionState(BattlePassProgress.PROGRESSION_IN_PROGRESS)
        battlePassModel.setIsBattlePassPurchased(battlePassData['hasBattlePass'])
        battlePassModel.setHasExtra(hasExtra)
        battlePassModel.setBattlePassState(state)
        battlePassModel.setSeasonNum(seasonNum)

    def __setLeaderboard(self, leaderboardModel):
        leaderboard = self.__data.get(BRSections.LEADERBOARD)
        if leaderboard is None:
            raise SoftException("There is no players' table in battle results")
        if self.__isSquadMode():
            vehiclesBySquad = {}
            for vehicle in leaderboard:
                vehiclesBySquad.setdefault(vehicle['squadIdx'], []).append(vehicle)

            placesData = vehiclesBySquad.values()
        else:
            placesData = []
            for vehicle in leaderboard:
                placesData.append([vehicle])

        placesData.sort(key=lambda v: v[0]['place'])
        groupList = leaderboardModel.getPlacesList()
        groupList.clear()
        for placeData in placesData:
            placeModel = PlaceModel()
            placeModel.setPlace(str(placeData[0]['place']))
            placeModel.setIsSquadMode(self.__isSquadMode())
            rowList = placeModel.getPlayersList()
            rowList.clear()
            for rowData in placeData:
                rowModel = RowModel()
                if rowData['isPersonal']:
                    rowModel.setType(LeaderboardConstants.ROW_TYPE_BR_PLAYER)
                elif rowData['isPersonalSquad']:
                    rowModel.setType(LeaderboardConstants.ROW_TYPE_BR_PLATOON)
                else:
                    rowModel.setType(LeaderboardConstants.ROW_TYPE_BR_ENEMY)
                rowModel.setAnonymizerNick(rowData['hiddenName'])
                self.__setUserName(rowModel.user, rowData)
                rowModel.user.setKills(rowData['kills'])
                rowModel.user.setDamage(rowData['damage'])
                rowModel.user.setVehicleLevel(rowData['achievedLevel'])
                rowModel.user.setVehicleType(rowData['vehicleType'])
                rowModel.user.setVehicleName(rowData['vehicleName'])
                rowList.addViewModel(rowModel)

            rowList.invalidate()
            groupList.addViewModel(placeModel)

        groupList.invalidate()
        return

    def __getFinishReason(self):
        isWinner = self.__data[BRSections.COMMON]['playerPlace'] == _THE_BEST_PLACE
        isWinnerPlace = self.__data[BRSections.COMMON]['playerPlace'] in (2, 3, 4, 5)
        isInSquad = self.__data[BRSections.COMMON]['isSquadMode']
        if isWinner:
            finishReason = R.strings.battle_royale.battleResult.title.victoryFirst()
        elif isWinnerPlace:
            finishReason = R.strings.battle_royale.battleResult.title.victoryOther()
        elif isInSquad:
            finishReason = R.strings.battle_royale.battleResult.title.squadDestroyed()
        else:
            finishReason = R.strings.battle_royale.battleResult.title.vehicleDestroyed()
        return finishReason

    def __isSquadMode(self):
        return self.__data[BRSections.COMMON]['isSquadMode']

    def __hasPremium(self):
        return self.__data[BRSections.COMMON]['hasPremium']

    def __getStats(self):
        return self.__data[BRSections.PERSONAL][BRSections.STATS]

    def __getFinancialData(self, section):
        financialData = self.__data.get(BRSections.PERSONAL, {}).get(section, {})
        return financialData

    def __getBattlePassPointsTotal(self):
        questsBonuses = self.__data[BRSections.PERSONAL][BRSections.REWARDS].get(BRSections.BONUSES)
        questPoints = sum([ bonus.getCount() for bonuses in questsBonuses for bonus in bonuses if bonus.getName() == 'battlePassPoints' ]) if questsBonuses else 0
        return self.__data[BRSections.PERSONAL][BRSections.BATTLE_PASS]['bpTopPoints'] + questPoints

    def __setFinishResult(self, personalResultsModel):
        finishReason = self.__getFinishReason()
        personalResultsModel.setFinishResultLabel(finishReason)

    def __setStats(self, statsModel):
        statsInfo = self.__getStats()
        if statsInfo is None:
            raise SoftException("There is no player's efficiency in battle results")
        statList = statsModel.getStatsList()
        statList.clear()
        for statData in statsInfo:
            statModel = StatItemModel()
            statModel.setType(statData['type'])
            statModel.setWreathImage(statData.get('wreathImage', R.invalid()))
            statModel.setCurrentValue(statData['value'])
            statModel.setMaxValue(statData['maxValue'])
            statList.addViewModel(statModel)

        statList.invalidate()
        return

    def __setBattleRewards(self, rewardsModel):
        rewardList = rewardsModel.getBattleRewardsList()
        rewardList.clear()
        rewards = self.__getEarnedRewards(BRSections.FINANCE)
        for reward in rewards:
            rewardList.addViewModel(reward)

        rewardList.invalidate()

    def __setBattleRewardsWithPremium(self, rewardsModel):
        rewardList = rewardsModel.getBattleRewardsListWithPremium()
        rewardList.clear()
        rewards = self.__getEarnedRewards(BRSections.FINANCE_PREM)
        for reward in rewards:
            rewardList.addViewModel(reward)

        rewardList.invalidate()

    def __setIsPlatoonWindowOpen(self, isOpen):
        with self.viewModel.transaction() as model:
            model.playerBattleTypeStatus.setIsPlatoonWindowOpen(isOpen)

    def __getBrProgressionTokenCount(self):
        total = 0
        rewardsSection = self.__data.get(BRSections.PERSONAL, {}).get(BRSections.REWARDS, {})
        awardTokens = rewardsSection.get(BRSections.BR_AWARD_TOKENS, {})
        total += self.__parseProgressionTokenCount(awardTokens)
        bonusesData = rewardsSection.get(BRSections.BONUSES, {})
        for questBonuses in bonusesData:
            for bonus in questBonuses:
                total += parseTokenBonusCount(bonus, self.__brProgressionController.progressionToken)

        return total

    def __getEarnedRewards(self, section):
        earned = self.__getFinancialData(section)
        if self.__brController.isBattlePassAvailable(self.__arenaBonusType):
            earned.update({BattleRewardItemModel.BATTLE_PASS_POINTS: self.__getBattlePassPointsTotal()})
        if self.__brProgressionController.isEnabled:
            progressionTokensEarned = self.__getBrProgressionTokenCount()
            if progressionTokensEarned:
                earned[BattleRewardItemModel.BR_PROGRESSION_TOKEN] = progressionTokensEarned
        sortedEarned = OrderedDict(sorted(earned.iteritems(), key=lambda x: _BATTLE_REWARD_TYPES.index(x[0])))
        financialList = []
        for bonusType, value in sortedEarned.iteritems():
            if value > 0 or bonusType not in _HIDDEN_BONUSES_WITH_ZERO_VALUES:
                statModel = BattleRewardItemModel()
                statModel.setType(bonusType)
                statModel.setValue(value)
                financialList.append(statModel)

        return financialList

    def __setCommonInfo(self):
        commonData = self.__data.get(BRSections.COMMON)
        if commonData is None:
            raise SoftException('There is no common info in battle results')
        model = self.viewModel.personalResults
        self.viewModel.personalResults.setPlace(commonData['playerPlace'])
        vehicleInfo = first(commonData['playerVehicles'])
        model.setVehicleName(vehicleInfo['vehicleName'])
        model.setVehicleType(vehicleInfo['vehicleType'])
        model.setHasPremium(self.__hasPremium())
        return

    def __setMapName(self):
        commonData = self.__data.get(BRSections.COMMON, {})
        self.viewModel.setMapName(commonData.get('arenaStr', ''))

    def __setCompletedQuests(self, personalModel):
        questsCount = self.__data[BRSections.PERSONAL][BRSections.REWARDS].get('completedQuestsCount', 0)
        personalModel.setQuestCompleted(questsCount)

    def __getTooltipParametersCreator(self):
        return {TooltipConstantsModel.ACHIEVEMENT_TOOLTIP: self.__getAchievementTooltipParameters,
         TooltipConstantsModel.QUEST_COMPLETE_TOOLTIP: self.__getQuestsTooltipParameters,
         TooltipConstantsModel.BONUS_TOOLTIP: self.__getBonusTooltipParameters}

    def __getAchievementTooltipParameters(self, event):
        achievementName = event.getArgument('achievementName')
        if achievementName is None:
            raise SoftException('There is no achievement info in tooltip arguments')
        return createTooltipData(isSpecial=True, specialAlias=TooltipConstantsModel.ACHIEVEMENT_TOOLTIP, specialArgs=[0,
         achievementName,
         False,
         [],
         0,
         0])

    def __getQuestsTooltipParameters(self, _):
        completedQuestIDs = self.__data[BRSections.PERSONAL][BRSections.REWARDS]['completedQuests'].keys()
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_ROYALE_COMPLETED_QUESTS_INFO, specialArgs=[HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON, completedQuestIDs])

    def __getBonusTooltipParameters(self, event):
        _, bonusID = event.getArgument('tooltipId', '').split(':')
        tooltipData = self.__tooltipsData.get(bonusID)
        return None if tooltipData is None else tooltipData

    @staticmethod
    def __normalizeTooltipID(tooltipID):
        return TooltipConstantsModel.BONUS_TOOLTIP if tooltipID.startswith(TooltipConstantsModel.BONUS_TOOLTIP) else tooltipID

    def __parseProgressionTokenCount(self, tokens):
        return tokens.get(self.__brProgressionController.progressionToken, {}).get('count', 0)

    @staticmethod
    def __setUserName(model, info):
        model.setUserName(info.get('userName', ''))
        model.setDatabaseID(info.get('databaseID', 0))
        model.setClanAbbrev(info.get('clanAbbrev', info.get('userClanAbbrev', '')))
        model.setHiddenUserName(info.get('hiddenName', ''))

    def __isCommander(self):
        return self.prbEntity is not None and self.prbEntity.isCommander()

    def __isTournament(self):
        return self.__arenaBonusType in _TOURNAMENT_ARENA_BONUS_TYPES
