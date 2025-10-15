# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/battle_result/portal_battle_result_view.py
from constants import FINISH_REASON
from debug_utils import LOG_WARNING
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showHangar
from gui.impl.pub import ViewImpl
from gui.battle_results import reusable
from helpers import dependency
from portal.gui.impl.lobby.tooltips.progress_token_tooltip import ProgressTokenTooltip
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IHangarFeatureStateController
from skeletons.gui.shared import IItemsCache
from portal_common.portal_constants import PortalBattleLevel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.portal_battle_result_view_model import PortalBattleResultViewModel, FinishResultType
from portal.gui.impl.gen.view_models.views.lobby.battle_result.player_results.battle_reward_item_model import BattleRewardItemModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.leader_board.row_model import RowModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.player_results.stat_item_model import StatItemModel
from portal.gui.impl.lobby.tooltips.battle_result_stat_tooltip import BattleResultStatTooltip
from portal.skeletons.portal_event_controller import IPortalEventController
from portal.sounds.sound_constants import PortalMusicState, PORTAL_BATTLE_RESULT_SOUND_SPACE

def _getFinishTypeDescr(finishType, wavesCount=0, wavesDone=0):
    FINISH_TYPE_TO_DESCRIPTION = {FinishResultType.TIME_OUT_DEFEAT: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.timeOut(), wavesCount=wavesCount, wavesDone=wavesDone),
     FinishResultType.TECHNICAL_DEFEAT: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.technicalDefeat(), wavesCount=wavesCount, wavesDone=wavesDone),
     FinishResultType.DEFAULT_WIN: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.defaultWin()),
     FinishResultType.SUPER_BOSS_WIN: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.ratteDestroyed()),
     FinishResultType.PLAYER_BASE_CAPTURED_DEFEAT: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.baseCaptured(), wavesCount=wavesCount, wavesDone=wavesDone)}
    return FINISH_TYPE_TO_DESCRIPTION.get(finishType, u'')


def _getFinishType(finishReason, battleDifficulty):

    def getFinishTypeFromExterminationReason(difficulty):
        return FinishResultType.SUPER_BOSS_WIN if difficulty == PortalBattleLevel.MASTER else FinishResultType.DEFAULT_WIN

    FINISH_REASON_TO_FINISH_TYPE = {FINISH_REASON.EXTERMINATION: getFinishTypeFromExterminationReason(battleDifficulty),
     FINISH_REASON.BASE: FinishResultType.PLAYER_BASE_CAPTURED_DEFEAT,
     FINISH_REASON.TIMEOUT: FinishResultType.TIME_OUT_DEFEAT,
     FINISH_REASON.TECHNICAL: FinishResultType.TECHNICAL_DEFEAT}
    return FINISH_REASON_TO_FINISH_TYPE.get(finishReason)


BATTLE_REWARDS_ORDER = [BattleRewardItemModel.UPGRADE_POINTS, BattleRewardItemModel.PROGRESSION_POINTS]

class PortalBattleResultView(ViewImpl):
    __slots__ = ('__data', '__arenaUniqueID', '__reusable')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __portalController = dependency.descriptor(IPortalEventController)
    __hangarFeatureStateController = dependency.descriptor(IHangarFeatureStateController)
    __cache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = PORTAL_BATTLE_RESULT_SOUND_SPACE

    def __init__(self, layoutID, arenaUniqueID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = PortalBattleResultViewModel()
        super(PortalBattleResultView, self).__init__(settings)
        self.__arenaUniqueID = arenaUniqueID
        self.__data = self.__battleResults.getResultsVO(self.__arenaUniqueID) or {}
        self.__reusable = None
        reusableRaw = self.__data.get('reusable')
        if reusableRaw:
            self.__reusable = reusable.createReusableInfo(reusableRaw)
        return

    @property
    def viewModel(self):
        return super(PortalBattleResultView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.portal.lobby.tooltips.BattleResultStatTooltip():
            name = event.getArgument('name')
            return BattleResultStatTooltip(name)
        if contentID == R.views.portal.lobby.tooltips.ProgressTokenTooltip():
            isTokeTooltip = event.getArgument('isTokenTooltip')
            return ProgressTokenTooltip(isTokeTooltip, True, -1, -1)
        return super(PortalBattleResultView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(PortalBattleResultView, self)._initialize(*args, **kwargs)
        self.viewModel.onClose += self.__onClose

    def _finalize(self):
        self.__hangarFeatureStateController.exit(self.layoutID)
        self.__portalController.showComplexityUnlock()
        self.viewModel.onClose -= self.__onClose
        self.__data = None
        self.__reusable = None
        super(PortalBattleResultView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(PortalBattleResultView, self)._onLoading(*args, **kwargs)
        if self.__battleResults and self.__data:
            with self.viewModel.transaction() as model:
                self.__setCommonInfo(model)
                self.__setPlayersResult(model.playerResultsModel)
                self.__setLeaderBoard(model.leaderboardModel)

    def _onLoaded(self, *args, **kwargs):
        self.__hangarFeatureStateController.enter(self.layoutID, doHideHeader=True)

    @property
    def __avatarData(self):
        return self.__data['results']['personal']['avatar']

    @property
    def __commonResults(self):
        return self.__data['results']['common']

    @property
    def __vehiclesResults(self):
        return self.__data['results']['vehicles']

    @property
    def __playerStats(self):
        return self.__data['personal']['stats']

    def __setPlayersResult(self, model):
        self.__setStats(model)
        self.__setEarnedRewards(model)

    def __setLeaderBoard(self, model):
        resultList = model.getPlacesList()
        resultList.clear()
        leaderBoard = self.__data['leaderboard']
        for playerInfo in sorted(leaderBoard, key=lambda p: p['place']):
            rowModel = RowModel()
            rowModel.setPlace(playerInfo['place'])
            rowModel.setIsPersonal(playerInfo['isPersonal'])
            rowModel.setIsSquadMode(playerInfo['isSquadMode'])
            rowModel.setSquadIndex(playerInfo['squadIdx'])
            rowModel.user.setUserName(playerInfo['userName'])
            rowModel.user.setDatabaseID(playerInfo['databaseID'])
            rowModel.user.setClanAbbrev(playerInfo['clanAbbrev'])
            rowModel.user.setHiddenUserName(playerInfo['hiddenName'])
            rowModel.user.setKills(playerInfo['kills'])
            rowModel.user.setDamage(playerInfo['damage'])
            rowModel.user.setDamageBlocked(playerInfo['damageBlocked'])
            rowModel.user.setVehicleType(playerInfo['vehicleType'])
            rowModel.user.setVehicleName(playerInfo['vehicleName'])
            dbID = playerInfo['databaseID']
            vehicleLevel = self.__getVehicleLevelByDBID(dbID)
            rowModel.user.setVehicleLevel(vehicleLevel)
            isLeaver = self.__isCurPlayerLeaver(dbID)
            rowModel.setIsLeaver(isLeaver)
            resultList.addViewModel(rowModel)

        resultList.invalidate()

    def __setCommonInfo(self, model):
        commonData = self.__data.get('common', {})
        battleDuration = commonData.get('duration', '')
        arenaDateTime = commonData.get('arenaCreateTimeStr', '')
        battleLevel = self.__data.get('portalBattleLevel', PortalBattleLevel.EASY)
        playerTeam = self.__avatarData['team']
        winnerTeam = self.__commonResults['winnerTeam']
        isWin = playerTeam == winnerTeam
        finishReason = self.__commonResults['finishReason']
        finishType = _getFinishType(finishReason, battleLevel)
        wavesDone = self.__getWavesDone()
        waveCount = self.__avatarData['wavesCount']
        finishReasonDescr = _getFinishTypeDescr(finishType, wavesCount=waveCount, wavesDone=wavesDone)
        accountDBID = self.__avatarData['accountDBID']
        vehID = self.__reusable.vehicles.getVehicleID(accountDBID)
        vehIntCD = self.__reusable.vehicles.getVehicleInfo(vehID).intCD
        vehicle = self.__cache.items.getItemByCD(vehIntCD)
        clanName = commonData['clanNameStr']
        playerName = commonData['playerRealNameStr']
        model.setBattleDuration(battleDuration)
        model.setArenaStartDateTime(arenaDateTime)
        model.setBattleDifficulty(battleLevel)
        if not isWin:
            PortalMusicState.setState(PortalMusicState.RESULT_SCREEN_DEFEAT)
            model.setFinishResultTitle(R.strings.portal_battle.finalStatistics.commonStats.resultlabel.lose())
        else:
            PortalMusicState.setState(PortalMusicState.RESULT_SCREEN_WIN)
            model.setFinishResultTitle(R.strings.portal_battle.finalStatistics.commonStats.resultlabel.win())
        model.setFinishResultType(finishType)
        model.setFinishResultDescr(finishReasonDescr)
        model.setPlayerVehicleName(vehicle.userName)
        model.setPlayerName(playerName)
        model.setClanAbbrev(clanName)

    def __setStats(self, model):
        statList = model.getStatsList()
        statList.clear()
        for statData in self.__playerStats:
            statModel = StatItemModel()
            statModel.setDescription(statData['type'])
            statModel.setWreathImage(statData.get('wreathImage', R.invalid()))
            statModel.setValue(statData['value'])
            statList.addViewModel(statModel)

        statList.invalidate()

    def __setEarnedRewards(self, model):
        rewardList = model.getBattleRewardsList()
        rewardList.clear()
        for rewardType in BATTLE_REWARDS_ORDER:
            rewardItemModel = BattleRewardItemModel()
            rewardItemModel.setType(rewardType)
            rewardItemModel.setValue(self.__getRewardAmount(rewardType))
            rewardList.addViewModel(rewardItemModel)

        rewardList.invalidate()

    def __getVehicleLevelByDBID(self, dbID):
        for vehicleInfo in self.__vehiclesResults.itervalues():
            if dbID == vehicleInfo[0]['accountDBID']:
                return vehicleInfo[0]['portalTankLevel']

        LOG_WARNING('Could not find a proper vehicle with databaseID = {}'.format(dbID))

    def __isCurPlayerLeaver(self, dbID):
        for vehicleInfo in self.__vehiclesResults.itervalues():
            if dbID == vehicleInfo[0]['accountDBID']:
                return vehicleInfo[0]['isPortalBattleLeave']

        LOG_WARNING('Could not find a proper vehicle with databaseID = {}'.format(dbID))
        return False

    def __getRewardAmount(self, rewardType):
        return self.__avatarData.get(rewardType, 0)

    def __getWavesDone(self):
        curWave = self.__avatarData['currentWave']
        isWavesCompleted = self.__avatarData['isCurrentWaveCompleted']
        return curWave if isWavesCompleted else curWave - 1

    def __onClose(self):
        showHangar()
        self.destroyWindow()
