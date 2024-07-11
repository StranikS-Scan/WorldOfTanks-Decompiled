# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_post_battle_view.py
import logging
import BigWorld
import typing
import SoundGroups
from races.gui.impl.gen.view_models.views.lobby.races_post_battle_view_model import RacesPostBattleViewModel, QuestsState
from races.gui.impl.lobby.races_lobby_view.ui_packers import fillQuestsModel
from races.skeletons.progression_controller import IRacesProgressionController
from races_common.races_common import checkIfViolator, RacesScoreEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import getNationLessName
from helpers import dependency
from helpers import time_utils
from shared_utils import findFirst, first
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IRacesBattleController
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Any, Dict, Tuple, Callable, Optional, Sequence
    import Event
    from races.gui.impl.gen.view_models.views.lobby.player_information import PlayerInformation
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.server_events.event_items import Quest

class RacesPostBattleView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('_battleResultsData', '__tooltipData')
    WIN_POSITIONS = (1, 2, 3)
    WIN_SOUND = 'ev_race_2024_resultscreen_win'
    LOOSE_SOUND = 'ev_race_2024_resultscreen_loose'
    __battleResults = dependency.descriptor(IBattleResultsService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __progressionCtrl = dependency.descriptor(IRacesProgressionController)
    __racesBattleCtrl = dependency.descriptor(IRacesBattleController)
    _notificationMgr = dependency.descriptor(INotificationWindowController)

    def __init__(self, layoutID, *args, **kwargs):
        self.__tooltipData = {}
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = RacesPostBattleViewModel()
        super(RacesPostBattleView, self).__init__(settings, *args, **kwargs)
        arenaUniqueID = kwargs.get('ctx', {}).get('arenaUniqueID')
        self._battleResultsData = self.__battleResults.getResultsVO(arenaUniqueID)

    @property
    def viewModel(self):
        return super(RacesPostBattleView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RacesPostBattleView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            data = self.__tooltipData.get(tooltipId)
            if isinstance(data, unicode):
                data = createTooltipData(tooltip=data)
            return data

    def _onLoading(self, *args, **kwargs):
        _logger.debug('[RacesPostBattleView] onLoading')
        super(RacesPostBattleView, self)._onLoading(*args, **kwargs)
        if self.__battleResults is not None and self._battleResultsData:
            self.__playSound()
            with self.viewModel.transaction() as model:
                playerId = BigWorld.player().databaseID
                model.setPlayerId(playerId)
                model.setPlayerNickname(self._battleResultsData.results['players'][playerId]['name'])
                model.setBattleFinishDate(self._battleResultsData.results['common'].get('arenaCreateTime', 0) + self._battleResultsData.results['common'].get('duration', 0))
                self._fillPlayersList(model)
                self._fillQuestsList(model)
        return

    def _initialize(self, *args, **kwargs):
        _logger.debug('[RacesPostBattleView] initialize')
        super(RacesPostBattleView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader()

    def _finalize(self):
        _logger.debug('[RacesPostBattleView] finalize')
        self.resumeLobbyHeader()
        self._notificationMgr.releasePostponed()
        super(RacesPostBattleView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),)

    def onClose(self):
        _logger.debug('[RacesPostBattleView] close button clicked')
        self.destroyWindow()
        self.__racesBattleCtrl.selectRaces()

    def __compareVehicles(self, veh1, veh2):
        disqvl1 = self.__getIsDisqualification(veh1['accountDBID'])
        disqvl2 = self.__getIsDisqualification(veh2['accountDBID'])
        if disqvl1 or disqvl2:
            if disqvl1 and disqvl2:
                return cmp(veh1['position'], veh2['position'])
            if disqvl2:
                return -1
            return 1
        finishFail1 = self.__getIsFinishFail(veh1)
        finishFail2 = self.__getIsFinishFail(veh2)
        if finishFail1 or finishFail2:
            if finishFail1 and finishFail2:
                return cmp(veh1['position'], veh2['position'])
            if finishFail2:
                return -1
            return 1
        return cmp(veh1['position'], veh2['position'])

    def _getSortedVehiclesData(self):
        vehicles = [ vehicleData[0] for vehicleData in self._battleResultsData.results['vehicles'].values() ]
        vehicles = sorted(vehicles, cmp=self.__compareVehicles)
        return vehicles

    def __getIsFinishFail(self, vehicleData):
        return vehicleData['racesScore/' + RacesScoreEvents.FINISH.name] == 0

    def __getIsDisqualification(self, accountDBId):
        return checkIfViolator(self._battleResultsData.results['avatars'][accountDBId])

    def __playSound(self):
        position = self.__getPlayerPosition()
        sound = self.WIN_SOUND if position in self.WIN_POSITIONS else self.LOOSE_SOUND
        SoundGroups.g_instance.playSound2D(sound)

    def __getPlayerPosition(self):
        playerID = BigWorld.player().databaseID
        vehData = findFirst(lambda data: first(data, {}).get('accountDBID') == playerID, self._battleResultsData.results['vehicles'].itervalues(), {})
        return first(vehData, {}).get('position', 0)

    def _fillPlayersList(self, model):
        vehicleDatas = self._getSortedVehiclesData()
        players = model.getPlayers()
        players.clear()
        players.reserve(len(vehicleDatas))
        for vehData in vehicleDatas:
            isDisqualified = self.__getIsDisqualification(vehData['accountDBID'])
            playerInfoModel = RacesPostBattleViewModel.getPlayersType()()
            playerInfoModel.setPlayerId(vehData['accountDBID'])
            playerInfoModel.setPlayerNickname(self._battleResultsData.results['players'][vehData['accountDBID']]['name'])
            playerInfoModel.setIsFinishFail(self.__getIsFinishFail(vehData))
            playerInfoModel.setIsDisqualification(isDisqualified)
            playerInfoModel.setPlace(vehData['position'])
            playerInfoModel.setRaceDuration(vehData['finishTime'])
            vehicle = self.__itemsCache.items.getItemByCD(vehData['typeCompDescr'])
            playerInfoModel.setVehicleName(vehicle.shortUserName)
            playerInfoModel.setVehicleIconName(getNationLessName(vehicle.name))
            if not isDisqualified:
                playerInfoModel.setPoints(vehData['racesTotalScore'])
                playerInfoModel.battleResultPoints.setBattles(vehData['racesScore/' + RacesScoreEvents.FINISH.name])
                playerInfoModel.battleResultPoints.setShot(vehData['racesScore/' + RacesScoreEvents.SHOT.name])
                playerInfoModel.battleResultPoints.setRamming(vehData['racesScore/' + RacesScoreEvents.RAMMING.name])
                playerInfoModel.battleResultPoints.setBoost(vehData['racesScore/' + RacesScoreEvents.BOOST.name])
                playerInfoModel.battleResultPoints.setShield(vehData['racesScore/' + RacesScoreEvents.SHIELD.name])
                playerInfoModel.battleResultPoints.setPowerImpulse(vehData['racesScore/' + RacesScoreEvents.POWER_IMPULSE.name])
            players.addViewModel(playerInfoModel)

    def _fillQuestsList(self, model):
        modelDailyQuests = model.getDailyQuests()
        modelDailyQuests.clear()
        self.__tooltipData = {}
        if self.__getIsDisqualification(BigWorld.player().databaseID):
            model.setQuestsState(QuestsState.NOPOINTS)
            return
        vehDescr = self._battleResultsData.results['common']['accountCompDescr'][BigWorld.player().databaseID][0][0]
        questsProgress = self._battleResultsData.results['personal'][vehDescr]['questsProgress']
        filteredQuestsProgress = {k:v for k, v in questsProgress.iteritems() if self.__progressionCtrl.isRacesProgressionQuest(k)}
        if not len(filteredQuestsProgress):
            dailyQuests = self.__progressionCtrl.collectSortedDailyQuests()
            allQuestsCompleted = all((q.isCompleted() for q in dailyQuests.itervalues()))
            if allQuestsCompleted:
                endSeasonDateSeconds = self.__racesBattleCtrl.getCurrentSeason().getEndDate()
                isLastDay = endSeasonDateSeconds - time_utils.getServerUTCTime() < time_utils.ONE_DAY
                if isLastDay:
                    model.setQuestsState(QuestsState.ALLQUESTSCOMPLETED)
                else:
                    model.setQuestsState(QuestsState.ALLQUESTSCOMPLETEDDAILY)
            else:
                model.setQuestsState(QuestsState.NOCOMLETEDQUESTS)
            return
        model.setQuestsState(QuestsState.HASCOMPLETEDQUESTS)
        quests = self.__progressionCtrl.collectSortedDailyQuests()
        questsWithProgress = {k:v for k, v in quests.iteritems() if k in filteredQuestsProgress}
        fillQuestsModel(model.getDailyQuests(), questsWithProgress, self.__tooltipData)
