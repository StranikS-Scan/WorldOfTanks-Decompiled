# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_royale/battle_result_view.py
from collections import defaultdict, OrderedDict
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.battle_result_view_model import BattleResultViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.battle_royale.battle_result_view.tooltip_constants_model import TooltipConstantsModel
from gui.impl.auxiliary.battle_royale.battle_result_view_base import BrBattleResultsViewBase
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from gui.shared.events import LobbyHeaderMenuEvent
from gui.server_events.battle_royale_formatters import BRSections
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.lobby.event_progression.after_battle_reward_view_helpers import formatBonuses
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import first
from soft_exception import SoftException
from gui.sounds.ambients import BattleResultsEnv
from gui.game_control.br_battle_sounds import BREvents
_THE_BEST_PLACE = 1

class BrBattleResultsViewInLobby(BrBattleResultsViewBase):
    __slots__ = ('__arenaUniqueID', '__tooltipsData', '__tooltipParametersCreator')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __brController = dependency.descriptor(IBattleRoyaleController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __sound_env__ = BattleResultsEnv

    def __init__(self, *args, **kwargs):
        self.__arenaUniqueID = kwargs.get('ctx', {}).get('arenaUniqueID')
        if self.__arenaUniqueID is None:
            raise SoftException('There is not arenaUniqueID in battleResults context')
        settings = ViewSettings(R.views.lobby.battle_royale.BattleResultView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = BattleResultViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BrBattleResultsViewInLobby, self).__init__(settings, *args, **kwargs)
        self.__tooltipsData = {}
        self.__tooltipParametersCreator = self.__getTooltipParametersCreator()
        return

    @property
    def viewModel(self):
        return super(BrBattleResultsViewInLobby, self).getViewModel()

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

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
        BREvents.playSound(BREvents.BATTLE_SUMMARY_SHOW)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), scope=EVENT_BUS_SCOPE.LOBBY)
        event_dispatcher.hideSquadWindow()

    def _onLoading(self, *args, **kwargs):
        super(BrBattleResultsViewInLobby, self)._onLoading(*args, **kwargs)
        self._setTabsData(self.viewModel)

    def _finalize(self):
        BREvents.playSound(BREvents.BR_RESULT_PROGRESS_BAR_STOP)
        self.__tooltipsData = None
        self.__tooltipParametersCreator = None
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        super(BrBattleResultsViewInLobby, self)._finalize()
        return

    def _getData(self, **kwargs):
        return self.__battleResults.getResultsVO(self.__arenaUniqueID)

    def _getFinishReason(self):
        isWinner = self._data[BRSections.COMMON]['playerPlace'] == _THE_BEST_PLACE
        isInSquad = self._data[BRSections.COMMON]['isSquadMode']
        if isWinner:
            finishReason = R.strings.battle_royale.battleResult.title.victory()
        elif isInSquad:
            finishReason = R.strings.battle_royale.battleResult.title.squadDestroyed()
        else:
            finishReason = R.strings.battle_royale.battleResult.title.vehicleDestroyed()
        return finishReason

    def _getStats(self):
        return self._data[BRSections.PERSONAL][BRSections.STATS]

    def _getFinancialData(self):
        return self._data.get(BRSections.PERSONAL, {}).get(BRSections.FINANCE, {})

    def _setPersonalResult(self, personalModel):
        self.__setMapName()
        self.__setCommonInfo()
        super(BrBattleResultsViewInLobby, self)._setPersonalResult(personalModel)
        self.__setBonuses(personalModel)
        self.__setAchievements(personalModel)
        self.__setCompletedQuests(personalModel)
        self.__setProgress()

    def _fillLeaderboardGroups(self, leaderboard, groupList):
        settings = self.__lobbyContext.getServerSettings().battleRoyale
        if self._isSquadMode():
            brPointsByPlace = settings.eventProgression.get('brPointsChangesBySquadPlace', ())
            allGroups = self.__splitBySquadGroups(leaderboard, brPointsByPlace)
        else:
            brPointsByPlace = settings.eventProgression.get('brPointsChangesByPlace', ())
            allGroups = self.__splitBySoloGroups(leaderboard, brPointsByPlace)
        maxPoint = first(brPointsByPlace)
        if maxPoint not in allGroups.keys():
            self.__addEmptyGroup(allGroups, maxPoint)
        allGroups = OrderedDict(sorted(allGroups.iteritems(), key=lambda elem: elem[0], reverse=True))
        self.__processGroups(allGroups, groupList)

    def __processGroups(self, allGroups, groupList):
        if self._isSquadMode():
            for points, group in allGroups.iteritems():
                for place, innerGroup in group.iteritems():
                    isPersonalSquad = self.__isPersonalGroup(innerGroup)
                    self._fillLeaderbordGroup(groupList, self.__getSortedGroup(innerGroup), points, place, isPersonalSquad)

        else:
            for points, group in allGroups.iteritems():
                self._fillLeaderbordGroup(groupList, self.__getSortedGroup(group), points)

    def __setCommonInfo(self):
        commonData = self._data.get(BRSections.COMMON)
        if commonData is None:
            raise SoftException('There is no common info in battle results')
        model = self.viewModel.personalResults
        self.viewModel.personalResults.setPlace(commonData['playerPlace'])
        vehicleInfo = first(commonData['playerVehicles'])
        model.setNationName(vehicleInfo['nationName'])
        model.setVehicleName(vehicleInfo['vehicleName'])
        return

    def __setMapName(self):
        commonData = self._data.get(BRSections.COMMON, {})
        self.viewModel.setMapName(commonData.get('arenaStr', ''))

    def __setCompletedQuests(self, personalModel):
        questsCount = self._data[BRSections.PERSONAL][BRSections.REWARDS].get('completedQuestsCount', 0)
        personalModel.setQuestCompleted(questsCount)

    def __setBonuses(self, model):
        bonuses = self._data[BRSections.PERSONAL][BRSections.REWARDS].get(BRSections.BONUSES, {})
        if not bonuses:
            return
        bonusesModel = model.getBonuses()
        bonusesModel.clear()
        bonuses = [ bonus for bonus in formatBonuses(bonuses) if bonus.getName() not in self._CURRENCIES ]
        packBonusModelAndTooltipData(bonuses, bonusesModel, tooltipData=self.__tooltipsData)
        bonusesModel.invalidate()

    def __setAchievements(self, model):
        achievements = self._data[BRSections.PERSONAL][BRSections.REWARDS].get(BRSections.ACHIEVEMENTS, [])
        if not achievements:
            return
        achievementsList = model.getAchievements()
        achievementsList.clear()
        for achievementName in achievements:
            achievementModel = AchievementModel()
            achievementModel.setName(achievementName)
            achievementsList.addViewModel(achievementModel)

        achievementsList.invalidate()

    def __setProgress(self):
        progressionData = self._data.get(BRSections.PERSONAL, {}).get(BRSections.PROGRESS, {})
        earnedPoints = progressionData['earnedPoints']
        currentLevel = progressionData['currentLevel']
        if not progressionData or earnedPoints == 0 or currentLevel == self.__brController.getMaxPlayerLevel():
            return
        iconPath = R.images.gui.maps.icons.battleRoyale.battleResult.battle_reward.progress.br_points()
        model = self.viewModel.personalResults.progressModel
        model.setProgressStage(progressionData['progressStage'])
        model.setCurrentLevel(progressionData['currentLevel'])
        model.setNextLevel(progressionData['nextLevel'])
        model.setEarnedPoints(progressionData['earnedPoints'])
        model.setPointsIcon(iconPath)
        model.setProgressValue(progressionData['progressValue'])
        model.setProgressDelta(progressionData['progressDelta'])

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

    def __getQuestsTooltipParameters(self, event):
        completedQuestIDs = self._data.get('personal', {}).get('rewards', {}).get('completedQuests', {}).keys()
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_PROGRESSION_COMPLETED_QUESTS_INFO, specialArgs=[HANGAR_HEADER_QUESTS.QUEST_TYPE_COMMON, completedQuestIDs])

    def __getBonusTooltipParameters(self, event):
        _, bonusID = event.getArgument('tooltipId', '').split(':')
        tooltipData = self.__tooltipsData.get(bonusID)
        return None if tooltipData is None else tooltipData

    def __addEmptyGroup(self, allGroups, maxPoint):
        isSquad = self._isSquadMode()
        if isSquad:
            allGroups[maxPoint] = {}
            allGroups[maxPoint][_THE_BEST_PLACE] = []
        else:
            allGroups[maxPoint] = []
        return allGroups

    @classmethod
    def __splitBySoloGroups(cls, leaderboard, brPointsByPlace):
        groups = defaultdict(list)
        for player in leaderboard:
            points = cls.__getPoints(player['place'] - 1, brPointsByPlace)
            groups[points].append(player)

        return groups

    @classmethod
    def __splitBySquadGroups(cls, leaderboard, brPointsByPlace):
        squads = defaultdict(list)
        for player in leaderboard:
            squads[player['squadIdx']].append(player)

        groups = defaultdict(lambda : defaultdict(list))
        for squad in squads.values():
            place = min((player['place'] for player in squad))
            points = cls.__getPoints(place - 1, brPointsByPlace)
            groups[points][place].extend(squad)

        return {k:OrderedDict(sorted(value.items(), key=lambda elem: elem[0])) for k, value in groups.items()}

    @staticmethod
    def __getSortedGroup(group):
        return sorted(group, key=lambda player: player['place'])

    @staticmethod
    def __isPersonalGroup(group):
        return any([ player['isPersonal'] for player in group ])

    @staticmethod
    def __getPoints(place, brPointsByPlace):
        return brPointsByPlace[place] if place < len(brPointsByPlace) else 0

    @staticmethod
    def __normalizeTooltipID(tooltipID):
        return TooltipConstantsModel.BONUS_TOOLTIP if tooltipID.startswith(TooltipConstantsModel.BONUS_TOOLTIP) else tooltipID
