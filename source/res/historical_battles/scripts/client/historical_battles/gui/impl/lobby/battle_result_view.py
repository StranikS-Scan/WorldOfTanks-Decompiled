# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/battle_result_view.py
import typing
import logging
import BigWorld
from constants import DEATH_REASON_ALIVE
from historical_battles_common.helpers_common import getFrontCouponModifier
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.sounds.ambients import BattleResultsEnv
from gui.prb_control import prbEntityProperty
from helpers import dependency
from PlayerEvents import g_playerEvents
from historical_battles.gui.impl.lobby.tooltips.battle_result_progress_tooltip import BattleResultProgressTooltip
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from shared_utils import nextTick
from skeletons.gui.battle_results import IBattleResultsService
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import BaseTeamMemberModel, TeamMemberBanType
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_result_view_model import BattleResultViewModel, BattleResultType, BoosterType, FairplayStatus
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from historical_battles.gui.impl.lobby.tooltips.ability_tooltip import AbilityTooltip
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from historical_battles.gui.impl.lobby import HB_LOCK_SOURCE_NAME
from gui.shared.lock_overlays import lockNotificationManager
if typing.TYPE_CHECKING:
    from typing import Dict
    from HBAccountBattleResultCache import HBAccountBattleResultCache
    from HBFrontCouponsComponent import HBFrontCouponsComponent
_logger = logging.getLogger(__name__)

class ParamsBag(object):

    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def toDict(self):
        return self.__dict__


class BattleResultView(BaseEventView):
    __slots__ = ('__arenaUniqueID', '__vo', '__visibilityMenuState')
    __sound_env__ = BattleResultsEnv
    DESTROY_ON_EVENT_DISABLED = False
    battleResults = dependency.descriptor(IBattleResultsService)
    layoutID = R.views.historical_battles.lobby.BattleResultView()

    def __init__(self, layoutID, arenaUniqueID):
        settings = ViewSettings(layoutID or self.layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW)
        settings.model = BattleResultViewModel()
        self.__arenaUniqueID = arenaUniqueID
        self.__vo = None
        self.__visibilityMenuState = -1
        super(BattleResultView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattleResultView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.HB_EFFICIENCY_TOOLTIP and self.__vo:
                statType = event.getArgument('type', None)
                vo = self.__vo['details']
                bag = ParamsBag(type=statType)
                if statType == BATTLE_EFFICIENCY_TYPES.DAMAGE:
                    bag.update(values=vo['damageDealtVals'], discript=vo['damageDealtNames'], totalItemsCount=str(vo['damageTotalItems']))
                if statType == BATTLE_EFFICIENCY_TYPES.ASSIST:
                    bag.update(values=vo['damageAssistedVals'], discript=vo['damageAssistedNames'], totalAssistedDamage=str(vo['damageAssisted']))
                if statType == BATTLE_EFFICIENCY_TYPES.ARMOR:
                    bag.update(values=vo['armorVals'], discript=vo['armorNames'], totalItemsCount=str(vo['armorTotalItems']))
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=[bag]), self.getParentWindow())
                window.load()
                return window
        return super(BattleResultView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip():
            coinType = event.getArgument('coinType')
            if coinType is None:
                _logger.error('HbCoinTooltip must receive a viable coinType param. Received: None')
                return
            return HbCoinTooltip(coinType)
        elif contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            orderType = event.getArgument('orderType')
            showStatus = event.getArgument('showStatus')
            return OrderTooltip(orderType, showStatus)
        elif contentID == R.views.historical_battles.lobby.tooltips.AbilityTooltip():
            abilityID = event.getArgument('abilityID')
            return AbilityTooltip(abilityID)
        else:
            return BattleResultProgressTooltip(event.getArgument('frontName'), event.getArgument('icon')) if contentID == R.views.historical_battles.lobby.tooltips.BattleResultProgressTooltip() else super(BattleResultView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(BattleResultView, self)._onLoading(*args, **kwargs)
        self.__addEventListeners()
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__fillViewModel()
        else:
            nextTick(self.destroyWindow)()
        if not self._gameEventController.isHistoricalBattlesMode():
            inOutData = {'visibilityMenuState': -1}
            g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.ON_GET_VISIBILITY_MENU_STATE, ctx=inOutData), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__visibilityMenuState = inOutData['visibilityMenuState']
            self.updateHeaderMenu(HeaderMenuVisibilityState.NOTHING)

    def _finalize(self):
        lockNotificationManager(False, source=HB_LOCK_SOURCE_NAME)
        self.__removeEventListeners()
        if not self._gameEventController.isHistoricalBattlesMode() and self.__visibilityMenuState != -1:
            self.updateHeaderMenu(self.__visibilityMenuState)
            self.__visibilityMenuState = -1
        super(BattleResultView, self)._finalize()

    def __onClose(self, *_):
        self.destroyWindow()

    def __addEventListeners(self):
        self.viewModel.columnSettings.onSetSortBy += self.__onSetSortBy
        self.viewModel.onClose += self.__onClose
        self.viewModel.onApplyBooster += self.__onApplyBooster
        g_playerEvents.onDisconnected += self.__onClose
        g_playerEvents.onEnqueued += self.__onClose

    def __removeEventListeners(self):
        self.viewModel.columnSettings.onSetSortBy -= self.__onSetSortBy
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onApplyBooster -= self.__onApplyBooster
        g_playerEvents.onDisconnected -= self.__onClose
        g_playerEvents.onEnqueued -= self.__onClose

    def __handleBattleResultsPosted(self, reusableInfo, _, __):
        if self.__arenaUniqueID == reusableInfo.arenaUniqueID:
            Waiting.hide('stats')
            self.__fillViewModel()

    @args2params(str)
    def __onSetSortBy(self, column):
        previous = self.viewModel.columnSettings.getSortBy()
        with self.viewModel.transaction() as tx:
            tx.columnSettings.setSortBy(column)
            if previous == column:
                tx.columnSettings.setSortDirection(not tx.columnSettings.getSortDirection())
            else:
                tx.columnSettings.setSortDirection(True)

    def __fillViewModel(self):
        vo = self.battleResults.getResultsVO(self.__arenaUniqueID)
        self.__handleBattleViolations(vo)
        self.__vo = vo
        with self.viewModel.transaction() as tx:
            self.__fillCommonInfo(tx, vo)
            self.__fillTeam(tx, vo)
            self.__fillEarnings(tx, vo)
            self.__fillBattleInfo(tx, vo)
            self.__fillPlayerInfo(tx, vo)
        if self._gameEventController.isEnabled():
            self.__handleFrontCoupons()

    def __handleBattleViolations(self, vo):
        if vo['fairplayStatus'] is not FairplayStatus.PLAYER:
            vo['damageAssisted'] = 0
            vo['damageDone'] = 0
            vo['damageBlocked'] = 0
            vo['kills'] = 0

    def __handleFrontCoupons(self):

        def fillFrontCoupons(earnedCoins, appliedBooster):
            if not appliedBooster:
                return
            boosterType = self.__getBoosterType(appliedBooster)
            with self.viewModel.transaction() as tx:
                tx.earnings.setAmount(earnedCoins)
                tx.setBoosterType(boosterType)
                tx.setIsBoosterUsed(True)

        battleResultCache = BigWorld.player().HBAccountBattleResultCache
        battleResultCache.requestBattleResults(self.__arenaUniqueID, fillFrontCoupons)

    def __handleTeammateViolations(self, playerVO):
        if playerVO.get('violationName', TeamMemberBanType.NOTBANNED) is not TeamMemberBanType.NOTBANNED:
            playerVO['damageAssisted'] = 0
            playerVO['damageDealt'] = 0
            playerVO['damageBlocked'] = 0
            playerVO['kills'] = 0

    def __fillCommonInfo(self, model, vo):
        resultType = BattleResultType[vo['battleResultType'].upper()]
        model.setResultType(resultType)
        model.setFrontName(vo['frontName'])
        model.setFairplayStatus(vo['fairplayStatus'])
        if resultType == BattleResultType.WIN:
            model.setTitle(R.strings.hb_lobby.battleResults.title.victory())
            model.setSubTitle(R.strings.hb_lobby.battleResults.subTitle.allTasksCompleted())
        elif resultType == BattleResultType.TIE:
            model.setTitle(R.strings.hb_lobby.battleResults.title.draw())
            model.setSubTitle(vo['finishReason'])
        else:
            model.setTitle(R.strings.hb_lobby.battleResults.title.lose())
            model.setSubTitle(vo['finishReason'])
        boosterType = BoosterType.EMPTY
        boosterCount = 0
        battleResultCache = BigWorld.player().HBAccountBattleResultCache
        if battleResultCache.activeArenaID == self.__arenaUniqueID:
            frontCouponsComponent = BigWorld.player().HBFrontCouponsComponent
            activeFrontCoupon = frontCouponsComponent.getFrontCouponByID(battleResultCache.activeBooster)
            if activeFrontCoupon:
                boosterType = self.__getBoosterType(activeFrontCoupon.getFrontCouponID())
                boosterCount = activeFrontCoupon.getCurrentCount()
        model.setBoosterType(boosterType)
        model.setBoosterCount(boosterCount)
        model.setIsBoosterUsed(False)
        columns = model.columnSettings.getVisibleColumns()
        columns.clear()
        for column in ['damage',
         'kills',
         'assist',
         'blocked']:
            columns.addString(column)

        columns.invalidate()
        model.columnSettings.setSortBy('damage')
        model.columnSettings.setSortDirection(True)

    def __fillTeam(self, model, vo):
        team = model.getTeam()
        team.clear()
        for i, playerVO in enumerate(vo['players']):
            team.addViewModel(self.__createTeamMember(i, playerVO))

        team.invalidate()

    def __createTeamMember(self, index, playerVO):
        self.__handleTeammateViolations(playerVO)
        member = BaseTeamMemberModel()
        member.setId(index)
        member.setIsCurrentPlayer(playerVO['isSelf'])
        member.setIsOwnSquad(playerVO['isSelf'] or playerVO['isOwnSquad'])
        member.setIsAlive(True)
        member.setSquadNum(playerVO['squadID'])
        member.setBanType(playerVO.get('violationName', TeamMemberBanType.NOTBANNED))
        member.stats.setAssist(playerVO['damageAssisted'])
        member.stats.setDamage(playerVO['damageDealt'])
        member.stats.setBlocked(playerVO['damageBlocked'])
        member.stats.setKills(playerVO['kills'])
        member.user.setIsFakeNameVisible(False)
        member.user.setUserName(playerVO['userVO']['userName'])
        member.user.setClanAbbrev(playerVO['userVO']['clanAbbrev'])
        member.user.badge.setBadgeID('' if playerVO['badgeID'] == 0 else str(playerVO['badgeID']))
        member.vehicle.setVehicleName(playerVO['vehicleName'])
        member.vehicle.setVehicleType(playerVO['tankType'])
        member.setLevel(playerVO['divisionLevel'])
        return member

    def __fillEarnings(self, model, vo):
        model.earnings.setAmount(vo['earnings']['amount'])
        model.earnings.setType(vo['earnings']['type'])

    def __fillBattleInfo(self, model, vo):
        model.battleInfo.setModeName(R.strings.hb_lobby.battleResults.mode.dyn(vo['frontName'])())
        model.battleInfo.setMapName(vo['map']['name'])
        model.battleInfo.setMapId(vo['map']['id'])
        model.battleInfo.setStartDate(vo['common']['arenaCreateTimeStr'])
        model.battleInfo.setDuration(vo['duration'])
        model.battleInfo.setMissionProgressLabel(R.strings.hb_lobby.battleResults.missionProgress.allTasksLabel())

    def __fillPlayerInfo(self, model, vo):
        model.playerInfo.user.setUserName(vo['playerName'])
        model.playerInfo.user.setClanAbbrev(vo['playerClan'])
        model.playerInfo.vehicle.setVehicleName(vo['tankName'])
        model.playerInfo.vehicle.setVehicleType(vo['tankType'])
        playerVehicles = vo['common']['playerVehicles']
        hasAliveVehicle = any([ vehicle['deathReason'] == DEATH_REASON_ALIVE for vehicle in playerVehicles ])
        isPrematureLeaved = any([ vehicle['isPrematureLeave'] for vehicle in playerVehicles ])
        model.playerInfo.setIsKilled(not hasAliveVehicle)
        if isPrematureLeaved:
            model.playerInfo.setIsKilled(True)
            model.playerInfo.setReason('premature_leave')
        elif not hasAliveVehicle:
            model.playerInfo.setReason('division_vehicles_exterminated')
        model.playerInfo.setTasksAmount(vo['arenaPhases']['total'])
        model.playerInfo.setTasksCompleted(vo['arenaPhases']['current'])
        model.playerInfo.stats.setKills(vo['kills'])
        model.playerInfo.stats.setDamage(vo['damageDone'])
        model.playerInfo.stats.setAssist(vo['damageAssisted'])
        model.playerInfo.stats.setBlocked(vo['damageBlocked'])

    def __getBoosterType(self, frontCouponID):
        modifier = getFrontCouponModifier(frontCouponID) if frontCouponID else None
        if not modifier:
            return BoosterType.EMPTY
        else:
            frontCouponStr = 'X{}'.format(modifier)
            return BoosterType[frontCouponStr]

    def __onApplyBooster(self):
        if not self._gameEventController.isEnabled():
            return
        player = BigWorld.player()
        battleResultCache = player.HBAccountBattleResultCache
        if battleResultCache.activeArenaID != self.__arenaUniqueID:
            _logger.warning("Can't apply booster on an inactive arena")
            return
        activeFrontCouponID = battleResultCache.activeBooster
        if not activeFrontCouponID:
            _logger.warning('No active front coupon found')
            return
        boosterType = self.viewModel.getBoosterType()
        if boosterType != self.__getBoosterType(activeFrontCouponID):
            _logger.warning('Mismatch of front coupons')
            return
        battleResultCache.applyBooster(self.__arenaUniqueID, activeFrontCouponID, self.__handleFrontCoupons)


class BattleResultViewWindow(LobbyWindow):

    def __init__(self, layoutID, arenaUniqueID):
        super(BattleResultViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=BattleResultView(layoutID, arenaUniqueID=arenaUniqueID))
