# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_royale/battle_result_view.py
import typing
from collections import OrderedDict
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.battle_result_view_model import BattleResultViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.tooltip_constants_model import TooltipConstantsModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.stat_item_model import StatItemModel
from gui.impl.gen.view_models.views.battle_royale.battle_results.leaderboard.leaderboard_constants import LeaderboardConstants
from gui.impl.gen.view_models.views.battle_royale.battle_results.personal.battle_reward_item_model import BattleRewardItemModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.place_model import PlaceModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.row_model import RowModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.battle_pass_progress import BattlePassProgress
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from gui.shared.events import LobbyHeaderMenuEvent
from gui.server_events.battle_royale_formatters import BRSections
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.lobby.event_progression.after_battle_reward_view_helpers import formatBonuses
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattleRoyaleController, IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import first
from soft_exception import SoftException
from gui.sounds.ambients import BattleResultsEnv
from gui.game_control.br_battle_sounds import BREvents
from constants import ATTACK_REASON_INDICES, ATTACK_REASON, DEATH_REASON_ALIVE
from gui.server_events import events_dispatcher
from gui.impl.lobby.battle_royale.tooltips.battle_pass_points_sources_tooltip_view import BattlePassPointsSourcesTooltipView
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.battle_royale.battle_results.player_vehicle_status_model import PlayerVehicleStatusModel
    from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.leaderboard_model import LeaderboardModel

def _getAttackReason(vehicleState, hasKiller):
    if vehicleState == DEATH_REASON_ALIVE:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.alive()
    elif vehicleState == ATTACK_REASON_INDICES[ATTACK_REASON.DEATH_ZONE]:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.reason.deathByZone()
    elif hasKiller:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.reason.deathByPlayer()
    else:
        reason = R.strings.battle_royale.battleResult.playerVehicleStatus.reason.other()
    return reason


_THE_BEST_PLACE = 1
_BR_POINTS_ICON = R.images.gui.maps.icons.battleRoyale.battleResult.leaderboard.br_selector_16()
_CURRENCIES = [BattleRewardItemModel.XP,
 BattleRewardItemModel.CREDITS,
 BattleRewardItemModel.BATTLE_PASS_POINTS,
 BattleRewardItemModel.CRYSTALS]
_HIDDEN_BONUSES_WITH_ZERO_VALUES = frozenset([BattleRewardItemModel.CRYSTALS, BattleRewardItemModel.BATTLE_PASS_POINTS])

class BrBattleResultsViewInLobby(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__tooltipsData', '__tooltipParametersCreator', '__data')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __brController = dependency.descriptor(IBattleRoyaleController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __sound_env__ = BattleResultsEnv

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_royale.BattleResultView())
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
        self.__tooltipsData = {}
        self.__tooltipParametersCreator = self.__getTooltipParametersCreator()
        return

    @property
    def viewModel(self):
        return super(BrBattleResultsViewInLobby, self).getViewModel()

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    def createToolTipContent(self, event, contentID):
        return BattlePassPointsSourcesTooltipView(self.__data) if event.contentID == R.views.lobby.battle_royale.tooltips.BattlePassPointsSourcesTooltipView() else super(BrBattleResultsViewInLobby, self).createToolTipContent(event, contentID)

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

    def _initialize(self, *args, **kwargs):
        super(BrBattleResultsViewInLobby, self)._initialize(*args, **kwargs)
        self.viewModel.personalResults.battlePassProgress.onSubmitClick += self.__onBattlePassClick
        self.__brController.onUpdated += self.__updateBattlePass
        BREvents.playSound(BREvents.BATTLE_SUMMARY_SHOW)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), scope=EVENT_BUS_SCOPE.LOBBY)
        event_dispatcher.hideSquadWindow()

    def _finalize(self):
        BREvents.playSound(BREvents.BR_RESULT_PROGRESS_BAR_STOP)
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.bp_progress_bar_stop()))
        self.__tooltipsData = None
        self.__tooltipParametersCreator = None
        self.__data = None
        self.__brController.onUpdated -= self.__updateBattlePass
        self.viewModel.personalResults.battlePassProgress.onSubmitClick -= self.__onBattlePassClick
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        super(BrBattleResultsViewInLobby, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(BrBattleResultsViewInLobby, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__setPlayerVehicleStatus(model.playerVehicleStatus)
            self.__setPersonalResult(model.personalResults)
            self.__setLeaderboard(model.leaderboardModel)

    def __onBattlePassClick(self):
        events_dispatcher.showMissionsBattlePassCommonProgression()

    def __updateBattlePass(self):
        self.__setBattlePass(self.viewModel.personalResults.battlePassProgress)
        self.__setBattleRewards(self.viewModel.personalResults)

    def __setPlayerVehicleStatus(self, statusModel):
        commonInfo = self.__data.get(BRSections.COMMON)
        if commonInfo is None:
            raise SoftException('There is no vehicle status info in battle results')
        statusInfo = commonInfo['vehicleStatus']
        self.__setUserName(statusModel.user, commonInfo)
        killerInfo = statusInfo['killer']
        hasKiller = killerInfo and not statusInfo['isSelfDestroyer']
        statusModel.setReason(_getAttackReason(statusInfo.get('vehicleState', ''), hasKiller))
        if hasKiller:
            self.__setUserName(statusModel.killer, killerInfo)
        return

    def __setPersonalResult(self, personalModel):
        self.__setMapName()
        self.__setCommonInfo()
        self.__setFinishResult(personalModel)
        self.__setStats(personalModel)
        self.__setBattleRewards(personalModel)
        self.__setBonuses(personalModel)
        self.__setAchievements(personalModel)
        self.__setCompletedQuests(personalModel)
        self.__setBattlePass(personalModel.battlePassProgress)

    def __setBattlePass(self, battlePassModel):
        battlePassData = self.__data[BRSections.PERSONAL][BRSections.BATTLE_PASS]
        totalPoints = self.__getBattlePassPointsTotal()
        battlePassModel.setEarnedPoints(min(totalPoints, battlePassData['currentLevelPoints']))
        battlePassModel.setCurrentLevel(battlePassData['currentLevel'])
        battlePassModel.setMaxPoints(battlePassData['maxPoints'])
        battlePassModel.setCurrentLevelPoints(battlePassData['currentLevelPoints'])
        if battlePassData['isDone']:
            battlePassModel.setProgressionState(BattlePassProgress.PROGRESSION_COMPLETED)
        else:
            battlePassModel.setProgressionState(BattlePassProgress.PROGRESSION_IN_PROGRESS)
        state = BattlePassProgress.BP_STATE_DISABLED
        if self.__brController.isBattlePassAvailable():
            state = BattlePassProgress.BP_STATE_BOUGHT if self.__battlePassController.isBought() else BattlePassProgress.BP_STATE_NORMAL
        battlePassModel.setBattlePassState(state)

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
                rowModel.user.setVehicleNation(rowData['nationName'])
                rowModel.user.setVehicleName(rowData['vehicleName'])
                rowList.addViewModel(rowModel)

            rowList.invalidate()
            groupList.addViewModel(placeModel)

        groupList.invalidate()
        return

    def __getFinishReason(self):
        isWinner = self.__data[BRSections.COMMON]['playerPlace'] == _THE_BEST_PLACE
        isInSquad = self.__data[BRSections.COMMON]['isSquadMode']
        if isWinner:
            finishReason = R.strings.battle_royale.battleResult.title.victory()
        elif isInSquad:
            finishReason = R.strings.battle_royale.battleResult.title.squadDestroyed()
        else:
            finishReason = R.strings.battle_royale.battleResult.title.vehicleDestroyed()
        return finishReason

    def __isSquadMode(self):
        return self.__data[BRSections.COMMON]['isSquadMode']

    def __getStats(self):
        return self.__data[BRSections.PERSONAL][BRSections.STATS]

    def __getFinancialData(self):
        financialData = self.__data.get(BRSections.PERSONAL, {}).get(BRSections.FINANCE, {})
        if self.__brController.isBattlePassAvailable():
            financialData.update({BattleRewardItemModel.BATTLE_PASS_POINTS: self.__getBattlePassPointsTotal()})
        return financialData

    def __getBattlePassPointsTotal(self):
        questsBonuses = self.__data[BRSections.PERSONAL][BRSections.REWARDS].get(BRSections.BONUSES)
        questPoints = sum([ bonus.getValue() for bonuses in questsBonuses for bonus in bonuses if bonus.getName() == 'battlePassPoints' ]) if questsBonuses else 0
        return self.__data[BRSections.PERSONAL][BRSections.BATTLE_PASS]['earnedPoints'] + questPoints

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
        rewards = self.__getEarnedFinance()
        for reward in rewards:
            rewardList.addViewModel(reward)

        rewardList.invalidate()

    def __getEarnedFinance(self):
        earned = self.__getFinancialData()
        sortedEarned = OrderedDict(sorted(earned.iteritems(), key=lambda x: _CURRENCIES.index(x[0])))
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
        model.setNationName(vehicleInfo['nationName'])
        model.setVehicleName(vehicleInfo['vehicleName'])
        return

    def __setMapName(self):
        commonData = self.__data.get(BRSections.COMMON, {})
        self.viewModel.setMapName(commonData.get('arenaStr', ''))

    def __setCompletedQuests(self, personalModel):
        questsCount = self.__data[BRSections.PERSONAL][BRSections.REWARDS].get('completedQuestsCount', 0)
        personalModel.setQuestCompleted(questsCount)

    def __setBonuses(self, model):
        bonuses = self.__data[BRSections.PERSONAL][BRSections.REWARDS].get(BRSections.BONUSES, {})
        if not bonuses:
            return
        bonusesModel = model.getBonuses()
        bonusesModel.clear()
        bonuses = [ bonus for bonus in formatBonuses(bonuses) if bonus.getName() not in _CURRENCIES ]
        packBonusModelAndTooltipData(bonuses, bonusesModel, tooltipData=self.__tooltipsData)
        bonusesModel.invalidate()

    def __setAchievements(self, model):
        achievements = self.__data[BRSections.PERSONAL][BRSections.REWARDS].get(BRSections.ACHIEVEMENTS, [])
        if not achievements:
            return
        achievementsList = model.getAchievements()
        achievementsList.clear()
        for achievementName in achievements:
            achievementModel = AchievementModel()
            achievementModel.setName(achievementName)
            achievementsList.addViewModel(achievementModel)

        achievementsList.invalidate()

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

    @staticmethod
    def __setUserName(model, info):
        model.setUserName(info.get('userName', ''))
        model.setClanAbbrev(info.get('clanAbbrev', info.get('userClanAbbrev', '')))
