# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/lobby/post_battle/post_battle_view.py
import typing
import re
from constants import IS_DEVELOPMENT
from shared_utils import first
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.sounds.ambients import BattleResultsEnv
from skeletons.gui.battle_results import IBattleResultsService
from grinch.gui.impl.gen.view_models.views.lobby.post_battle.post_battle_view_model import PostBattleViewModel, TeamPlaceIconEnum, TeamColorEnum
from grinch.gui.impl.gen.view_models.views.lobby.post_battle.score_item_model import ScoreItemModel, ScoreTypeEnum
from grinch.gui.impl.gen.view_models.views.lobby.post_battle.score_player_model import ScorePlayerModel
from grinch.gui.impl.gen.view_models.views.battle.grinch_player_model import VehicleTypeEnum
from grinch_progression.gui.impl.lobby.views.quests_helper import getWeekendQuests, VehicleRoleStr, getDailyModifiersQuest
from grinch_progression.gui.impl.lobby.views.quests_packer import getGrinchPostBattleUIDataPacker, calculatePrize
from grinch_common.grinch_constants import Teams, PLAYER_TEAMS, PLAYER_VEHICLE_TYPES
from items.vehicles import getVehicleClass
if typing.TYPE_CHECKING:
    from typing import Dict, Any, Sequence, Optional, List
    from gui.battle_results.reusable import _ReusableInfo
    from gui.server_events.event_items import Quest
_TEAM_PLACE_TO_ORDINAL_NUMBER = {1: TeamPlaceIconEnum.FIRST,
 2: TeamPlaceIconEnum.SECOND,
 3: TeamPlaceIconEnum.THIRD}
_TEAMS_TO_ENUM_VALUE = {Teams.CYAN: TeamColorEnum.CYAN,
 Teams.YELL: TeamColorEnum.YELLOW,
 Teams.MGNT: TeamColorEnum.MAGENTA}
_TANK_TO_ASSIST_POINTS = {VehicleTypeEnum.LIGHTTANK: 'grinch/abilityAssistBuffPoints',
 VehicleTypeEnum.MEDIUMTANK: 'grinch/abilityAssistFlarePoints',
 VehicleTypeEnum.HEAVYTANK: 'grinch/abilityAssistBlizzardPoints'}
_TANK_TO_ROLE = {VehicleTypeEnum.LIGHTTANK: VehicleRoleStr.CARRIER,
 VehicleTypeEnum.MEDIUMTANK: VehicleRoleStr.SUPPORT,
 VehicleTypeEnum.HEAVYTANK: VehicleRoleStr.ASSAULT}
_SCORING_TO_KEY = [(ScoreTypeEnum.DAMAGECAUSED, 'grinch/damagePoints'),
 (ScoreTypeEnum.DESTROYED, 'grinch/killPoints'),
 (ScoreTypeEnum.DAMAGEASSIST, 'grinch/hitAssistPoints'),
 (ScoreTypeEnum.BASEDEFENDED, 'grinch/baseDefenderBonusPoints'),
 (ScoreTypeEnum.DELIVERED, 'grinch/presentsDeliveryPoints'),
 (ScoreTypeEnum.SPOTTED, 'grinch/enemyDetectionPoints')]
MODIFIERS_QUEST_REGEX = re.compile('grinch:modifiers:.+')

class PostBattleView(ViewImpl):
    __slots__ = ('_battleResultsData',)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __sound_env__ = BattleResultsEnv

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.grinch.lobby.post_battle.PostBattleView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = PostBattleViewModel()
        super(PostBattleView, self).__init__(settings, *args, **kwargs)
        arenaUniqueID = kwargs.get('ctx', {}).get('arenaUniqueID')
        self._battleResultsData = self.__battleResults.getResultsVO(arenaUniqueID)

    @property
    def viewModel(self):
        return super(PostBattleView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onSelectedPlayerChange, self._onSelectedPlayerChange))

    def _onLoading(self, *args, **kwargs):
        super(PostBattleView, self)._onLoading(*args, **kwargs)
        if self.__battleResults is not None and self._battleResultsData:
            with self.viewModel.transaction() as model:
                self._setBattleOverTimestamp(model)
                self._setPlayersList(model)
                totalProgressionPointsEarned = self._fillQuests(model)
                self._setBattleResult(model, totalProgressionPointsEarned)
        return

    def _onClose(self):
        self.destroyWindow()

    def _iterateTeamsPlayers(self):
        teamPlayers = self.viewModel.getCyanPlayers()
        for playerScore in teamPlayers:
            yield (playerScore, teamPlayers)

        teamPlayers = self.viewModel.getYellowPlayers()
        for playerScore in teamPlayers:
            yield (playerScore, teamPlayers)

        teamPlayers = self.viewModel.getMagentaPlayers()
        for playerScore in teamPlayers:
            yield (playerScore, teamPlayers)

    def _onSelectedPlayerChange(self, selectedPlayer):
        playerName = selectedPlayer['selectedPlayerName']
        vehicleData = self._getVehicleByPlayerName(playerName)
        changedElements = 0
        changedTeams = set()
        for player, team in self._iterateTeamsPlayers():
            if player.getIsSelectedPlayer():
                player.setIsSelectedPlayer(False)
                changedTeams.add(team)
                changedElements += 1
            if player.getName() == playerName:
                player.setIsSelectedPlayer(True)
                changedTeams.add(team)
                changedElements += 1
            if changedElements == 2:
                break

        for team in changedTeams:
            team.invalidate()

        self._fillScoreList(self.viewModel, vehicleData)
        self.viewModel.getSelectedPlayerScoreItems().invalidate()

    def _getPlayerData(self):
        vehicleData = self._battleResultsData.results['personal'].values()
        playerData = vehicleData[0]
        playerData.update({'grinch/progressionPoints': vehicleData[1].get('grinch/progressionPoints')})
        return playerData

    def _getVehiclesByTeam(self, team):
        vehicleData = self._battleResultsData.results['vehicles']
        return sorted([ vehicleData[0] for vehicleData in vehicleData.values() if vehicleData[0]['team'] == team and getVehicleClass(vehicleData[0]['typeCompDescr']) in PLAYER_VEHICLE_TYPES ], key=lambda vehicle: vehicle['grinch/totalGrinchPoints'], reverse=True)

    def _getVehicleByPlayerName(self, name):
        vehicleData = self._battleResultsData.results['vehicles']
        players = self._getReusableData().players
        for vehicleData in vehicleData.values():
            playerName = players.getPlayerInfo(vehicleData[0]['accountDBID']).realName
            if name == playerName:
                return vehicleData[0]

    def _getCommonData(self):
        return self._battleResultsData.results['common']

    def _getReusableData(self):
        return self._battleResultsData.reusable

    def _setBattleOverTimestamp(self, model):
        commonData = self._getCommonData()
        battleTimestamp = commonData['arenaCreateTime'] + commonData['duration']
        model.setBattleOverTimestamp(battleTimestamp)

    def _setPlayersList(self, model):
        currentAccountDBID = self._getPlayerData()['accountDBID']
        teamToGetter = {Teams.CYAN: model.getCyanPlayers,
         Teams.YELL: model.getYellowPlayers,
         Teams.MGNT: model.getMagentaPlayers}
        teamsPlacement = {team:len(PLAYER_TEAMS) for team in PLAYER_TEAMS}
        for team in PLAYER_TEAMS:
            teamVehicles = self._getVehiclesByTeam(team)
            if IS_DEVELOPMENT and not teamVehicles:
                continue
            teamPlace = teamVehicles[0]['grinch/teamPlace']
            teamsPlacement[team] = teamPlace
            teamPlayers = teamToGetter[team]()
            teamPlayers.clear()
            teamPlayers.reserve(len(teamVehicles))
            for vehicleData in teamVehicles:
                playerModel = ScorePlayerModel()
                vehicleAccountID = vehicleData['accountDBID']
                self._fillPlayerModel(playerModel, vehicleData)
                if currentAccountDBID == vehicleAccountID:
                    self._fillPlayerModel(model.currentPlayer, vehicleData)
                    self._fillScoreList(model, vehicleData)
                    playerModel.setIsCurrentPlayer(True)
                    playerModel.setIsSelectedPlayer(True)
                teamPlayers.addViewModel(playerModel)

        teamOrder = model.getTeamOrder()
        teamOrder.clear()
        teamOrder.reserve(len(PLAYER_TEAMS))
        orderedTeams = sorted(teamsPlacement, key=teamsPlacement.get)
        for team in orderedTeams:
            teamOrder.addString(_TEAMS_TO_ENUM_VALUE[team].value)

    def _fillPlayerModel(self, playerModel, vehicleData):
        vehicleClass = getVehicleClass(vehicleData['typeCompDescr'])
        playerModel.setVehicle(VehicleTypeEnum(vehicleClass))
        info = self._getReusableData().players.getPlayerInfo(vehicleData['accountDBID'])
        playerModel.setPlatoon(info.squadIndex)
        playerModel.setName(info.realName)
        playerModel.setScore(vehicleData['grinch/totalGrinchPoints'])

    def _setBattleResult(self, model, totalProgressionPointsEarned):
        playerData = self._getPlayerData()
        totalProgressionPointsEarned += playerData['grinch/progressionPoints']
        model.setTeamPlace(_TEAM_PLACE_TO_ORDINAL_NUMBER[playerData['grinch/teamPlace']])
        model.setTeamColor(_TEAMS_TO_ENUM_VALUE[playerData['team']])
        model.setPlayerPlace(playerData['grinch/personalPlace'])
        model.setTotalCoinsEarned(totalProgressionPointsEarned)

    def _createScoreModel(self, scoringType, points):
        score = ScoreItemModel()
        score.setType(scoringType)
        score.setScore(points)
        return score

    def _fillScoreList(self, model, vehicleData):
        playerScore = model.getSelectedPlayerScoreItems()
        playerScore.clear()
        playerScore.reserve(len(_SCORING_TO_KEY) + 1)
        for scoringType, battleResultsKey in _SCORING_TO_KEY:
            playerScore.addViewModel(self._createScoreModel(scoringType, vehicleData[battleResultsKey]))

        assistPointsKey = _TANK_TO_ASSIST_POINTS[VehicleTypeEnum(getVehicleClass(vehicleData['typeCompDescr']))]
        abilityAssistPoints = vehicleData[assistPointsKey]
        playerScore.addViewModel(self._createScoreModel(ScoreTypeEnum.ABILITYASSIST, abilityAssistPoints))

    def _fillQuests(self, model):
        questsProgress = self._getPlayerData().get('questsProgress', {})
        quests = self.__getQuests(questsProgress)
        questsModel = model.getDailyQuests()
        questsModel.clear()
        questsModel.reserve(len(quests))
        totalPointsEarned = 0
        for quest in quests:
            _, __, currentProgress = questsProgress[quest.getID()]
            if currentProgress.get('bonusCount', 0):
                totalPointsEarned += calculatePrize(quest)
            matchObject = MODIFIERS_QUEST_REGEX.search(quest.getID())
            if matchObject:
                continue
            questModel = getGrinchPostBattleUIDataPacker(quest).pack()
            questsModel.addViewModel(questModel)

        return totalPointsEarned

    def __getQuests(self, questsProgress):
        playerData = self._getPlayerData()
        vehicleCompDescr = playerData['typeCompDescr']
        quests = getWeekendQuests(role=_TANK_TO_ROLE[VehicleTypeEnum(getVehicleClass(vehicleCompDescr))])
        quests.extend(getDailyModifiersQuest())
        progressedQuests = []
        for quest in quests:
            if quest.getID() in questsProgress:
                _, __, currentProgress = questsProgress[quest.getID()]
                if first(currentProgress.itervalues()):
                    progressedQuests.append(quest)

        return progressedQuests
