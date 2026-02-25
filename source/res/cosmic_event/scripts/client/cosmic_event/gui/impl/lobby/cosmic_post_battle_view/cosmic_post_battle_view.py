# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/cosmic_post_battle_view/cosmic_post_battle_view.py
import logging
import typing
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringModel, ScoringTypeEnum
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.cosmic_daily_missions import CosmicDailyMissions
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.cosmic_post_battle_view_model import CosmicPostBattleViewModel
from cosmic_sound import CosmicHangarSounds
from cosmic_event.cosmic_constants import COSMIC_VEHICLES_ROVER_ENUM
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from cosmic_event.gui.shared.scores import SCORE_EVENTS_TO_MODEL_ENUM, sortEvents, sortEventsByName
from cosmic_event.gui.impl.lobby.quest_helpers import fillDailyQuestModel
from cosmic_event.gui.impl.lobby.quest_packer import PostBattleDailyCosmicQuestUIDataPacker
from cosmic_event.gui.impl.lobby.tooltips.cosmic_lootbox_tooltip_extended import CosmicExtendedLootboxTooltip
from cosmic_event.gui.impl.gen.view_models.views.lobby.post_battle_view.player_entry import PlayerEntry
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import ICosmicEventBattleController
from skeletons.gui.battle_results import IBattleResultsService
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from gui.shared.gui_items.Vehicle import Vehicle
from gui.impl.pub import ViewImpl
from helpers import dependency
from debug_utils import LOG_ERROR
if typing.TYPE_CHECKING:
    from typing import Sequence, List, Dict, Tuple, Callable, Optional, Any
    from Event import Event
    from gui.battle_results.reusable import _ReusableInfo
    from gui.server_events.event_items import Quest
    from gui.server_events.conditions import Cumulativable
_logger = logging.getLogger(__name__)
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


def createScoreEventCollection(vehicleData, isDeserter):
    scoreEvents = []
    for eName, eValue in SCORE_EVENTS_TO_MODEL_ENUM.iteritems():
        scores = vehicleData['cosmicScore/' + eName.name]
        scoreEvents.append((eValue, scores))

    if not isDeserter:
        sortEvents(scoreEvents)
    else:
        sortEventsByName(scoreEvents)
    return scoreEvents


def _fillScoreList(playerScore, scoreEvents):
    playerScore.clear()
    playerScore.reserve(len(ScoringTypeEnum))
    for scoring in scoreEvents:
        playerScore.addViewModel(_createScoringInfo(scoring[0], scoring[1]))


class CosmicPostBattleView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('_battleResultsData', '__tooltipData')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __battleController = dependency.descriptor(ICosmicEventBattleController)
    __progressionController = dependency.descriptor(ICosmicEventProgressionController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.cosmic_event.lobby.cosmic_post_battle.CosmicPostBattleView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CosmicPostBattleViewModel()
        super(CosmicPostBattleView, self).__init__(settings, *args, **kwargs)
        arenaUniqueID = kwargs.get('ctx', {}).get('arenaUniqueID')
        self._battleResultsData = self.__battleResults.getResultsVO(arenaUniqueID)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(CosmicPostBattleView, self).getViewModel()

    def _getCommonData(self):
        return self._battleResultsData.results['common']

    def _getPersonalData(self):
        myTeamId = self._battleResultsData.results.get('personal', {}).get('avatar', {}).get('team')
        if myTeamId is None:
            return {}
        else:
            myVehicle = [ vehicle[0] for _, vehicle in self._battleResultsData.results['vehicles'].iteritems() if vehicle[0]['team'] == myTeamId ]
            if not myVehicle:
                return {}
            vehicleCompId = myVehicle[0]['typeCompDescr']
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

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            data = self.__tooltipData.get(tooltipId)
            return data

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(CosmicPostBattleView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            if lootBox.isExtendedTooltip():
                return CosmicExtendedLootboxTooltip(lootBox)
            return LootboxTooltip(lootBox)
        LOG_ERROR('Can not create a tooltip. Unsupported contentID {}'.format(contentID))
        return super(CosmicPostBattleView, self).createToolTipContent(event, contentID)

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
        model.setLootResearch(personalData['cosmicScore/LOOT_RESEARCHING'])
        model.setKillAmount(personalData['kills'])
        model.setKillStreak(personalData['cosmicBattleEvent/MAX_KILL_SERIES'])

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
        vehicles = sorted(vehicles, key=lambda x: (avatars.getAvatarInfo(x['accountDBID']).hasPenalties(), -x['cosmicTotalScore'], self._getReusableData().players.getPlayerInfo(x['accountDBID']).realName.lower()))
        for place, vehicleData in enumerate(vehicles, start=1):
            playerEntry = PlayerEntry()
            curVehicleAccountId = vehicleData['accountDBID']
            isDeserter = avatars.getAvatarInfo(curVehicleAccountId).hasPenalties()
            scoreEvents = createScoreEventCollection(vehicleData, isDeserter)
            self._fillPlayerEntry(playerEntry, scoreEvents, vehicleData, place, isDeserter)
            players.addViewModel(playerEntry)
            if currentAccountDBID == curVehicleAccountId:
                self._fillPlayerEntry(model.currentPlayerEntry, scoreEvents, vehicleData, place, isDeserter)

    def _fillPlayerEntry(self, playerEntry, scoreEvents, vehicleData, place, isDeserter):
        name = self._getReusableData().players.getPlayerInfo(vehicleData['accountDBID']).realName
        clan = self._getReusableData().players.getPlayerInfo(vehicleData['accountDBID']).clanAbbrev
        playerEntry.setPlayerName(name)
        playerEntry.setPlayerClan(clan)
        playerEntry.setTotalPoints(vehicleData['cosmicTotalScore'])
        playerEntry.setIsDeserter(isDeserter)
        vehicle = Vehicle(typeCompDescr=vehicleData['typeCompDescr'])
        vehicleEnum = COSMIC_VEHICLES_ROVER_ENUM.get(vehicle.typeDescr.name, COSMIC_VEHICLES_ROVER_ENUM['default'])
        playerEntry.setVehicle(vehicleEnum.value)
        playerScores = playerEntry.getPlayersScore()
        _fillScoreList(playerScores, scoreEvents)
        playerEntry.setPlace(place)
        return playerEntry

    def _setHasDailyQuests(self, model):
        currentQuests = self.__progressionController.collectSortedRelevantDailyQuests().values()
        if not currentQuests:
            _logger.info('No current quests')
        model.setHasDailyQuests(any((not quest.isCompleted() for quest in currentQuests)))

    def _fillQuestsList(self, model):
        quests = self._getRelevantDailyQuests()
        missionsModel = model.getDailyQuests()
        missionsModel.clear()
        missionsModel.reserve(len(quests))
        initialTooltipIndex = 0
        self.__tooltipData = {}
        for quest in quests:
            questUIPacker = PostBattleDailyCosmicQuestUIDataPacker(initialTooltipIndex, quest)
            fullQuestModel = questUIPacker.pack()
            questsBonusList = fullQuestModel.getBonuses()
            dailyQuestModel = CosmicDailyMissions()
            rewards = dailyQuestModel.getRewards()
            rewards.clear()
            rewards.reserve(len(questsBonusList))
            for bonus in questsBonusList:
                rewards.addViewModel(bonus)

            self.__tooltipData.update(questUIPacker.tooltipData)
            initialTooltipIndex += len(questUIPacker.tooltipData)
            fillDailyQuestModel(dailyQuestModel, fullQuestModel)
            self._setQuestProgress(dailyQuestModel, quest)
            self.__progressionController.setQuestProgressAsViewed(quest)
            missionsModel.addViewModel(dailyQuestModel)
            fullQuestModel.unbind()

        missionsModel.invalidate()

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
