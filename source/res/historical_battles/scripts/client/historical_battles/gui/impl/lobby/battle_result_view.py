# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/battle_result_view.py
import logging
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
from historical_battles.polygons_config import PolygonsConfigReader
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.gui.impl.lobby.tooltips.frontmen_tooltip import FrontmanTooltip
from skeletons.gui.battle_results import IBattleResultsService
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberRoleType, TeamMemberBanType
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_result_team_member_model import BattleResultTeamMemberModel
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_result_view_model import BattleResultViewModel, BattleResultType, BoosterType, FairplayStatus
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from historical_battles.gui.impl.lobby.tooltips.ability_tooltip import AbilityTooltip
from historical_battles.gui.shared.event_dispatcher import showHBHangar
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
_logger = logging.getLogger(__name__)

class ParamsBag(object):

    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def toDict(self):
        return self.__dict__


class BattleResultView(BaseEventView):
    __slots__ = ('__arenaUniqueID',)
    __sound_env__ = BattleResultsEnv
    DESTROY_ON_EVENT_DISABLED = False
    battleResults = dependency.descriptor(IBattleResultsService)
    layoutID = R.views.historical_battles.lobby.BattleResultView()

    def __init__(self, layoutID, arenaUniqueID):
        settings = ViewSettings(layoutID or self.layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW)
        settings.model = BattleResultViewModel()
        self.__arenaUniqueID = arenaUniqueID
        self.__frontmanPolygons = PolygonsConfigReader.readXml(PolygonsConfigReader.FRONTMANS_PATH)
        self.__vo = None
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
            if tooltipId == TOOLTIPS_CONSTANTS.EFFICIENCY_PARAM and self.__vo:
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
            isPreview = event.getArgument('isPreview')
            isUsedInBattle = event.getArgument('isUsedInBattle')
            return OrderTooltip(orderType, isPreview, isUsedInBattle)
        elif contentID == R.views.historical_battles.lobby.tooltips.AbilityTooltip():
            abilityID = event.getArgument('abilityID')
            isRoleAbility = event.getArgument('isRoleAbility')
            return AbilityTooltip(abilityID, isRoleAbility)
        elif contentID == R.views.historical_battles.lobby.tooltips.FrontmanTooltip():
            frontmanID = event.getArgument('frontmanID')
            showRoleAbility = event.getArgument('showRoleAbility')
            return FrontmanTooltip(frontmanID, showRoleAbility)
        else:
            return BattleResultProgressTooltip(event.getArgument('frontName')) if contentID == R.views.historical_battles.lobby.tooltips.BattleResultProgressTooltip() else super(BattleResultView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(BattleResultView, self)._onLoading(*args, **kwargs)
        self.__addEventListeners()
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__fillViewModel()
        else:
            Waiting.show('stats')
            self.battleResults.onResultPosted += self.__handleBattleResultsPosted

    def _finalize(self):
        self.__removeEventListeners()
        super(BattleResultView, self)._finalize()

    def __onClose(self, *_):
        hbCtrl = dependency.instance(IGameEventController)
        isShowingProgressionView = hbCtrl.isShowingProgressionView()
        isInQueue = self.prbEntity and self.prbEntity.isInQueue()
        if not isInQueue and not isShowingProgressionView:
            showHBHangar()
        self.destroyWindow()

    def __addEventListeners(self):
        self.viewModel.columnSettings.onSetSortBy += self.__onSetSortBy
        self.viewModel.onClose += self.__onClose
        g_playerEvents.onDisconnected += self.__onClose
        g_playerEvents.onEnqueued += self.__onClose

    def __removeEventListeners(self):
        self.viewModel.columnSettings.onSetSortBy -= self.__onSetSortBy
        self.viewModel.onClose -= self.__onClose
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
            self.__fillRewardInfo(tx, vo)
            self.__fillBattleInfo(tx, vo)
            self.__fillPlayerInfo(tx, vo)

    def __handleBattleViolations(self, vo):
        if vo['fairplayStatus'] is not FairplayStatus.PLAYER:
            vo['damageAssisted'] = 0
            vo['damageDone'] = 0
            vo['damageBlocked'] = 0
            vo['kills'] = 0

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
        else:
            model.setTitle(R.strings.hb_lobby.battleResults.title.battleFinished())
            model.setSubTitle(vo['finishReason'])
        booster = BoosterType[vo['frontCoupon']] if vo['frontCoupon'] else BoosterType.EMPTY
        model.setUsedBoosterType(booster)
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
        member = BattleResultTeamMemberModel()
        member.setId(index)
        member.setIsCurrentPlayer(playerVO['isSelf'])
        member.setIsOwnSquad(playerVO['isSelf'] or playerVO['isOwnSquad'])
        member.setIsAlive(playerVO['killerID'] == 0)
        member.setSquadNum(playerVO['squadID'])
        member.setBanType(playerVO.get('violationName', TeamMemberBanType.NOTBANNED))
        member.setRoleType(getattr(TeamMemberRoleType, playerVO['role'], TeamMemberRoleType.NONE))
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
        return member

    def __fillEarnings(self, model, vo):
        model.earnings.setAmount(vo['earnings']['amount'])
        model.earnings.setType(vo['earnings']['type'])

    def __fillRewardInfo(self, model, vo):
        model.rewardInfo.setIsAchieved(vo['roleAbility']['obtained'])
        model.rewardInfo.ability.setIconName(vo['roleAbility']['icon'])
        model.rewardInfo.ability.setId(vo['roleAbility']['id'])

    def __fillBattleInfo(self, model, vo):
        model.battleInfo.setModeName(R.strings.hb_lobby.battleResults.mode.offence())
        model.battleInfo.setMapName(vo['map']['name'])
        model.battleInfo.setMapId(vo['map']['id'])
        model.battleInfo.setStartDate(vo['common']['arenaCreateTimeStr'])
        model.battleInfo.setDuration(vo['duration'])
        model.battleInfo.setMissionProgressLabel(R.strings.hb_lobby.battleResults.missionProgress.allTasksLabel())
        model.battleInfo.setIsHeroVehicle(vo['isHeroVehicle'])

    def __fillPlayerInfo(self, model, vo):
        model.playerInfo.user.setUserName(vo['playerName'])
        model.playerInfo.user.setClanAbbrev(vo['playerClan'])
        model.playerInfo.vehicle.setVehicleName(vo['tankName'])
        model.playerInfo.vehicle.setVehicleType(vo['tankType'])
        model.playerInfo.setIsKilled(vo['isKilled'])
        model.playerInfo.setRoleType(getattr(TeamMemberRoleType, vo['frontman']['role'], TeamMemberRoleType.NONE))
        model.playerInfo.setReason(vo['deathReason'])
        model.playerInfo.killerVehicle.setVehicleName(vo['killerInfo']['name'])
        model.playerInfo.killerVehicle.setVehicleType(vo['killerInfo']['type'])
        frontmanId = vo['frontman']['id']
        model.playerInfo.setFrontManId(frontmanId)
        model.playerInfo.setPolygon(self.__frontmanPolygons.getPolygon(frontmanId))
        model.playerInfo.setTasksAmount(vo['arenaPhases']['total'])
        model.playerInfo.setTasksCompleted(vo['arenaPhases']['current'])
        model.playerInfo.stats.setKills(vo['kills'])
        model.playerInfo.stats.setDamage(vo['damageDone'])
        model.playerInfo.stats.setAssist(vo['damageAssisted'])
        model.playerInfo.stats.setBlocked(vo['damageBlocked'])


class BattleResultViewWindow(LobbyWindow):

    def __init__(self, layoutID, arenaUniqueID):
        super(BattleResultViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=BattleResultView(layoutID, arenaUniqueID=arenaUniqueID))
