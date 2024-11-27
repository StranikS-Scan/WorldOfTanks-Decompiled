# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/cosmic_post_battle_view/cosmic_post_battle_view.py
import logging
import typing
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringModel, ScoringTypeEnum
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.cosmic_daily_missions import CosmicDailyMissions
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.cosmic_post_battle_view_model import CosmicPostBattleViewModel
from cosmic_event.gui.impl.lobby.quest_helpers import fillDailyQuestModel, getDailyQuestModelFromQuest
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from cosmic_sound import CosmicHangarSounds
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.player_entry import PlayerEntry
if typing.TYPE_CHECKING:
    from typing import Sequence, Dict, Tuple, Callable, Optional, Any
    from Event import Event
    from gui.battle_results.reusable import _ReusableInfo
    from gui.server_events.event_items import Quest
    from gui.server_events.conditions import _Cumulativable
_logger = logging.getLogger(__name__)
_scoringToKey = [(ScoringTypeEnum.SHOT, 'cosmicScore/SHOT'),
 (ScoringTypeEnum.RAM, 'cosmicScore/RAMMING'),
 (ScoringTypeEnum.KILL, 'cosmicScore/KILL'),
 (ScoringTypeEnum.SCAN, 'cosmicScore/ARTIFACT_SCAN'),
 (ScoringTypeEnum.PICKUP, 'cosmicScore/PICKUP'),
 (ScoringTypeEnum.ABILITYHIT, 'cosmicScore/ABILITY_HIT')]
_rewardKeys = ['index',
 'name',
 'value',
 'isCompensation',
 'tooltipId',
 'tooltipContentId',
 'label']

def _createScoringInfo(scoringType, points):
    score = ScoringModel()
    score.setMarsPoints(points)
    score.setType(scoringType)
    return score


def _fillScoreList(playerScore, vehicleData):
    playerScore.clear()
    playerScore.reserve(len(_scoringToKey))
    for scoringType, battleResultsKey in _scoringToKey:
        playerScore.addViewModel(_createScoringInfo(scoringType, vehicleData[battleResultsKey]))


class CosmicPostBattleView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('_battleResultsData',)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __battleController = dependency.descriptor(ICosmicEventBattleController)
    __progressionController = dependency.descriptor(ICosmicEventProgressionController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.cosmic_event.lobby.cosmic_post_battle.CosmicPostBattleView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CosmicPostBattleViewModel()
        super(CosmicPostBattleView, self).__init__(settings, *args, **kwargs)
        arenaUniqueID = kwargs.get('ctx', {}).get('arenaUniqueID')
        self._battleResultsData = self.__battleResults.getResultsVO(arenaUniqueID)

    @property
    def viewModel(self):
        return super(CosmicPostBattleView, self).getViewModel()

    def _getCommonData(self):
        return self._battleResultsData.results['common']

    def _getPersonalData(self):
        vehicleCompId = self.__battleController.getEventVehicle().intCD
        return self._battleResultsData.results['personal'][vehicleCompId]

    def _getVehiclesData(self):
        vehicleData = self._battleResultsData.results['vehicles']
        return [ vehicleData[0] for vehicleData in vehicleData.values() ]

    def _getReusableData(self):
        return self._battleResultsData.reusable

    def _onClose(self):
        self.destroyWindow()

    def _getEvents(self):
        eventListeners = [(self.viewModel.onClose, self._onClose)]
        return eventListeners

    def _onLoading(self, *args, **kwargs):
        super(CosmicPostBattleView, self)._onLoading(*args, **kwargs)
        CosmicHangarSounds.playCosmicBattleResultsEnter()
        if self.__battleResults is not None and self._battleResultsData:
            with self.viewModel.transaction() as model:
                self._setBattleOverTimestamp(model)
                self._setMainScores(model)
                self._setPlayersList(model)
                self._fillQuestsList(model)
                self._setHasDailyQuests(model)
        return

    def _initialize(self, *args, **kwargs):
        super(CosmicPostBattleView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader()

    def _finalize(self):
        self.resumeLobbyHeader()
        super(CosmicPostBattleView, self)._finalize()

    def _setMainScores(self, model):
        personalData = self._getPersonalData()
        model.setTotalPoints(personalData['cosmicTotalScore'])
        model.setKillAmount(personalData['kills'])
        model.setPickupAmount(personalData['cosmicBattleEvent/PICKUP'])

    def _setBattleOverTimestamp(self, model):
        commonData = self._getCommonData()
        battleOver = commonData['arenaCreateTime'] + commonData['duration']
        model.setBattleOverTimestamp(battleOver)

    def _setPlayersList(self, model):
        currentAccountDBID = self._getPersonalData()['accountDBID']
        vehicles = self._getVehiclesData()
        avatars = self._getReusableData().avatars
        players = model.getPlayersList()
        players.clear()
        players.reserve(len(vehicles))
        vehicles = sorted(vehicles, key=lambda x: (not avatars.getAvatarInfo(x['accountDBID']).hasPenalties(), x['cosmicTotalScore']), reverse=True)
        for place, vehicleData in enumerate(vehicles, start=1):
            playerEntry = PlayerEntry()
            curVehicleAccountId = vehicleData['accountDBID']
            isDeserter = avatars.getAvatarInfo(curVehicleAccountId).hasPenalties()
            self._fillPlayerEntry(playerEntry, vehicleData, place, isDeserter)
            players.addViewModel(playerEntry)
            if currentAccountDBID == curVehicleAccountId:
                self._fillPlayerEntry(model.currentPlayerEntry, vehicleData, place, isDeserter)

    def _fillPlayerEntry(self, playerEntry, vehicleData, place, isDeserter):
        name = self._getReusableData().players.getPlayerInfo(vehicleData['accountDBID']).realName
        clan = self._getReusableData().players.getPlayerInfo(vehicleData['accountDBID']).clanAbbrev
        playerEntry.setPlayerName(name)
        playerEntry.setPlayerClan(clan)
        playerEntry.setTotalPoints(vehicleData['cosmicTotalScore'])
        playerEntry.setIsDeserter(isDeserter)
        playerScores = playerEntry.getPlayersScore()
        _fillScoreList(playerScores, vehicleData)
        playerEntry.setPlace(place)
        return playerEntry

    def _setHasDailyQuests(self, model):
        model.setHasDailyQuests(any((not quest.isCompleted() for quest in self.__progressionController.getDailyQuests().values())))

    def _fillQuestsList(self, model):
        quests = self._getRelevantDailyQuests()
        missionsModel = model.getDailyQuests()
        missionsModel.clear()
        missionsModel.reserve(len(quests))
        for quest in quests:
            dailyQuestModel = CosmicDailyMissions()
            fullQuestModel = getDailyQuestModelFromQuest(quest)
            fillDailyQuestModel(dailyQuestModel, fullQuestModel)
            self._setQuestProgress(dailyQuestModel, quest)
            bonusesData = fullQuestModel.getBonuses()
            rewards = dailyQuestModel.getRewards()
            rewards.clear()
            rewards.reserve(len(bonusesData))
            for bonus in bonusesData:
                rewards.addViewModel(bonus)

            self.__progressionController.setQuestProgressAsViewed(quest)
            missionsModel.addViewModel(dailyQuestModel)
            fullQuestModel.unbind()

    def _setQuestProgress(self, dailyQuestModel, quest):
        questsProgress = self._getPersonalData().get('questsProgress', {})
        _, __, currentProgress = questsProgress[quest.getID()]
        conditionItems = quest.bonusCond.getConditions().items
        condition = conditionItems[0]
        isQuestCompleted = currentProgress.get('bonusCount', 0) > 0
        currentProgressValue = currentProgress.get(condition.getKey())
        if not isQuestCompleted:
            dailyQuestModel.setCurrentProgress(currentProgressValue)
        else:
            dailyQuestModel.setCurrentProgress(condition.getTotalValue())
        dailyQuestModel.setCompleted(isQuestCompleted)

    def _getRelevantDailyQuests(self):
        quests = self.__progressionController.collectSortedDailyQuests()
        questsProgress = self._getPersonalData().get('questsProgress', {})
        affectedQuests = []
        for quest in quests.values():
            if quest.getID() in questsProgress:
                _, previousProgress, currentProgress = questsProgress[quest.getID()]
                condition = self._getQuestCondition(quest)
                if not condition:
                    continue
                isQuestCompleted = currentProgress.get('bonusCount', 0) > 0
                currentProgressValue = currentProgress.get(condition.getKey(), 0)
                previousProgressValue = previousProgress.get(condition.getKey(), 0)
                if isQuestCompleted or currentProgressValue != previousProgressValue:
                    affectedQuests.append(quest)

        return affectedQuests

    def _getQuestCondition(self, quest):
        conditionItems = quest.bonusCond.getConditions().items
        if not conditionItems:
            _logger.error("Quest has no conditions, can't work with it.")
            return
        if len(conditionItems) > 1:
            _logger.warning('Quest has more than one condition: number of conditions %s. Using first one.', len(conditionItems))
        return conditionItems[0]
