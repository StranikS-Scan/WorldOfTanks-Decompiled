# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/battle_result/portal_battle_result_view.py
import sys
from constants import FINISH_REASON
from debug_utils import LOG_WARNING
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.backport.backport_context_menu import BackportContextMenuWindow, createContextMenuData
from gui.impl.gen import R
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.shared.event_dispatcher import showHangar
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.impl.pub import ViewImpl
from gui.battle_results import reusable
from helpers import dependency, time_utils
from portal.gui.impl.lobby.tooltips.progress_token_tooltip import ProgressTokenTooltip
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.shared import IItemsCache
from portal_common.portal_constants import PortalBattleLevel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.portal_battle_result_view_model import PortalBattleResultViewModel, FinishResultType
from portal.gui.impl.gen.view_models.views.lobby.battle_result.player_results.battle_reward_item_model import BattleRewardItemModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.leader_board.row_model import RowModel
from portal.gui.impl.gen.view_models.views.lobby.battle_result.player_results.stat_item_model import StatItemModel
from portal.gui.impl.lobby.tooltips.battle_result_token_tooltip import BattleResultTokenTooltip
from portal.skeletons.portal_event_controller import IPortalEventController
from portal.sounds.sound_constants import PortalMusicState, PORTAL_BATTLE_RESULT_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState

def _getFinishTypeDescr(finishType, wavesCount=0, wavesDone=0):
    FINISH_TYPE_TO_DESCRIPTION = {FinishResultType.TIME_OUT_DEFEAT: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.timeOut(), wavesCount=wavesCount, wavesDone=wavesDone),
     FinishResultType.TECHNICAL_DEFEAT: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.technicalDefeat(), wavesCount=wavesCount, wavesDone=wavesDone),
     FinishResultType.DEFAULT_WIN: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.defaultWin()),
     FinishResultType.SUPER_BOSS_WIN: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.ratteDestroyed()),
     FinishResultType.PLAYER_BASE_CAPTURED_DEFEAT: backport.text(R.strings.portal_battle_result.result.finishReasonDescr.baseCaptured(), wavesCount=wavesCount, wavesDone=wavesDone)}
    return FINISH_TYPE_TO_DESCRIPTION.get(finishType, u'')


def _getFinishType(finishReason, battleDifficulty):

    def getFinishTypeFromExterminationReason(difficulty):
        return FinishResultType.SUPER_BOSS_WIN if difficulty == PortalBattleLevel.HARD else FinishResultType.DEFAULT_WIN

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
    __cache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)
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
        if contentID == R.views.portal.lobby.tooltips.ProgressTokenTooltip():
            isTokenTooltip = event.getArgument('isTokenTooltip')
            isCompleted = True
            currentPoints = -1
            nextLevelPoints = -1
            if not isTokenTooltip:
                currentVehicle = self.__portalController.getCurrentSelectedVehicle()
                currentPoints = self.__portalController.getVehicleExperience(currentVehicle)
                nextLevelPoints = 0
                maxUpgradeLevel = len(self.__portalController.getVehicleUpgradeNodes(currentVehicle))
                upgradeLevel = self.__portalController.getUpgradeLevel(currentVehicle)
                isCompleted = upgradeLevel == maxUpgradeLevel
                nodes = self.__portalController.getVehicleUpgradeNodes(currentVehicle)
                currentLevel = self.__portalController.getUpgradeLevel(currentVehicle)
                for _, (upgradeLevel, upgradeNodes) in enumerate(nodes.iteritems()):
                    if upgradeLevel == currentLevel:
                        researchedNodes = self.__portalController.getDeserializedUpgradeTreeLevel(currentVehicle, upgradeLevel)
                        researchedNodes = [ node for _, node in researchedNodes.iteritems() ]
                        for _, (_, _) in enumerate(zip(upgradeNodes['nodes'], researchedNodes)):
                            requiredExp = upgradeNodes['requiredPoints']
                            nextLevelPoints = requiredExp

                        break

            return ProgressTokenTooltip(isTokenTooltip, isCompleted, currentPoints, nextLevelPoints)
        if contentID == R.views.portal.lobby.tooltips.BattleResultTokenTooltip():
            isWinner = event.getArgument('isWinner')
            battleDifficulty = event.getArgument('battleDifficulty')
            return BattleResultTokenTooltip(isWinner, battleDifficulty)
        return super(PortalBattleResultView, self).createToolTipContent(event, contentID)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            databaseID = event.getArgument('databaseID')
            if not databaseID or self.__connectionMgr.databaseID == databaseID:
                return super(PortalBattleResultView, self).createContextMenu(event)
            hiddenUserName = event.getArgument('hiddenUserName')
            ctx = {'dbID': databaseID,
             'userName': hiddenUserName if hiddenUserName else event.getArgument('userName'),
             'vehicleCD': self.__getVehicleCDByDBID(databaseID)}
            contextMenuData = createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.BATTLE_RESULTS_USER, ctx)
            window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
            window.load()
            return window
        return super(PortalBattleResultView, self).createContextMenu(event)

    def _initialize(self, *args, **kwargs):
        super(PortalBattleResultView, self)._initialize(*args, **kwargs)
        self.viewModel.onClose += self.__onClose

    def _finalize(self):
        self.__portalController.showComplexityUnlock()
        self.viewModel.onClose -= self.__onClose
        self.__data = None
        self.__reusable = None
        self.updateVisibilityHangarHeaderMenu(isVisible=True)
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
        self.updateVisibilityHangarHeaderMenu(isVisible=False)

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
        for playerInfo in sorted(leaderBoard, key=lambda p: p['place'] or sys.maxint):
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
            avatarInfo = self.__reusable.avatars.getAvatarInfo(dbID)
            if avatarInfo is not None and avatarInfo.badge > 0:
                rowModel.user.badge.setBadgeID(str(avatarInfo.badge))
            resultList.addViewModel(rowModel)

        resultList.invalidate()
        return

    def __setCommonInfo(self, model):
        commonData = self.__data.get('common', {})
        battleDuration = self.__getBattleDuration(commonData.get('duration', ''))
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

    def __getBattleDuration(self, formattedDuration):
        duration = self.__commonResults.get('duration', 0)
        return backport.text(R.strings.menu.Time.timeValueWithSecs.lessMin(), sec=int(duration)) if duration < time_utils.ONE_MINUTE else formattedDuration

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

    def __getVehicleCDByDBID(self, dbID):
        if self.__reusable is None:
            return
        else:
            vehicleID = self.__reusable.vehicles.getVehicleID(dbID)
            return self.__reusable.vehicles.getVehicleInfo(vehicleID).intCD or None

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

    def updateVisibilityHangarHeaderMenu(self, isVisible=False):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING if not isVisible else HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
