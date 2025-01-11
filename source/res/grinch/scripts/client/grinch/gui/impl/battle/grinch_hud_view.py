# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/battle/grinch_hud_view.py
import logging
import time
import weakref
import BigWorld
from typing import TYPE_CHECKING
import GUI
from constants import ARENA_PERIOD
from frameworks.wulf import ViewFlags, ViewSettings
from grinch.cgf.presents import getScoreComponent
from grinch.cgf.ui import getHomebaseMarkerTransform
from grinch.gui.battle_control.controllers.hit_direction_control import GrinchHitDamagePull
from grinch.gui.impl.battle import getTeamColorModelData, getMarkerTypeModelData
from grinch.gui.impl.battle.abilities_panel_ctrl import AbilitiesPanelCtrl
from grinch.gui.impl.battle.players_panel_ctrl import PlayersPanelCtrl
from grinch.gui.impl.battle.tank_panel_ctrl import TankPanelCtrl
from grinch.gui.impl.gen.view_models.views.battle.grinch_damage_indicator_model import GrinchDamageIndicatorModel, DamageIndicatorTypeEnum
from grinch.gui.impl.gen.view_models.views.battle.grinch_hud_view_model import GrinchHudViewModel, AnnouncementIconEnum
from grinch.gui.impl.gen.view_models.views.battle.grinch_marker_model import GrinchMarkerModel
from grinch.gui.impl.gen.view_models.views.battle.team_score_model import TeamScoreModel
from grinch.gui.shared.events import BotOwnershipEvent, StackableEquipmentUpdateEvent, HomebaseMarkerEvent
from grinch_common.grinch_constants import PLAYER_TEAMS, Teams
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    import Event
    from typing import Optional, Any, Sequence, Tuple, Callable, Dict, List
    from skeletons.gui.battle_session import IArenaDataProvider
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
    from Math import Matrix

@replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def _generateTeamGuiOrder(sessionProvider=None):
    arenaDP = sessionProvider.getArenaDP()
    allyTeam = arenaDP.getAllyTeams()[0]
    ordered = [ enumItem.value for enumItem in PLAYER_TEAMS ]
    ordered.sort(key=lambda teamID: -1 if teamID == allyTeam else teamID)
    return tuple(ordered)


class GrinchHudView(ViewImpl, MethodsRules):
    __slots__ = ('__teamGuiOrder', '__playersPanelCtrl', '__tankPanelCtrl', '__abilitiesPanelCtrl')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(R.views.grinch.battle.GrinchHudView(), ViewFlags.VIEW, GrinchHudViewModel())
        super(GrinchHudView, self).__init__(settings)
        self.__teamGuiOrder = None
        self.__playersPanelCtrl = None
        self.__tankPanelCtrl = None
        self.__abilitiesPanelCtrl = None
        self._markersCtrl = GUI.WGMarkerPositionController()
        return

    @MethodsRules.delayable()
    def arenaLoadCompleted(self):
        pass

    @property
    def viewModel(self):
        return super(GrinchHudView, self).getViewModel()

    def _getListeners(self):
        listeners = [(BotOwnershipEvent.OWNERSHIP_STATE_CHANGED,
          self._onTurretDeployEvent,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (StackableEquipmentUpdateEvent.STACKABLE_EQUIPMENT_UPDATED,
          self._onTurretStacksUpdatedEvent,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (HomebaseMarkerEvent.HOMEBASE_MARKER_UPDATE,
          self._onHomebaseMarkerEvent,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]
        return listeners

    def showHint(self, text, subtext, showCountdown, countdown, icon):
        cd = time.time() + countdown if showCountdown else -1
        try:
            annoncementIcon = AnnouncementIconEnum(icon)
        except AttributeError:
            annoncementIcon = AnnouncementIconEnum.NONE

        self.viewModel.setIsAnnouncementVisible(True)
        self._updateHint(text, subtext, cd, annoncementIcon)

    def hideHint(self):
        self.viewModel.setIsAnnouncementVisible(False)

    def addHitDirection(self, idx, attackerMatrix, isPenetration):
        with self.viewModel.transaction() as model:
            indicatorModel = model.getDamageIndicators().getValue(idx)
            if indicatorModel.getType() != DamageIndicatorTypeEnum.NONE:
                return
            self._markersCtrl.add(indicatorModel.proxy, attackerMatrix)
            if isPenetration:
                indicatorModel.setType(DamageIndicatorTypeEnum.PENETRATION)
            else:
                indicatorModel.setType(DamageIndicatorTypeEnum.RICOCHET)

    def hideHitDirection(self, idx):
        with self.viewModel.transaction() as model:
            indicatorModel = model.getDamageIndicators().getValue(idx)
            indicatorModel.setType(DamageIndicatorTypeEnum.NONE)
            self._markersCtrl.remove(indicatorModel.proxy)

    def _updateHint(self, text, subtext, countdown, icon):
        self.viewModel.setAnnouncementCountdownTargetTime(countdown)
        self.viewModel.setAnnouncementHeading(text)
        self.viewModel.setAnnouncementHeadingAbove(subtext)
        self.viewModel.setAnnouncementIcon(icon)

    def _getEvents(self):
        events = []
        scoreCmp = getScoreComponent()
        if scoreCmp is not None:
            events.append((scoreCmp.onTeamScoreUpdated, self.__onTeamScoreUpdated))
            events.append((scoreCmp.onVehiclePointsUpdated, self.__onVehiclePointsUpdated))
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            events.append((vehicleCtrl.onVehicleStateUpdated, self.__onVehicleStateUpdated))
        events.append((g_playerEvents.onArenaPeriodChange, self._onArenaPeriodChange))
        return events

    def _onLoading(self, *args, **kwargs):
        super(GrinchHudView, self)._onLoading(*args, **kwargs)
        self.__teamGuiOrder = _generateTeamGuiOrder()
        self.__setup()

    def _finalize(self):
        if self.__playersPanelCtrl:
            self.__playersPanelCtrl.dispose()
            self.__playersPanelCtrl = None
        if self.__tankPanelCtrl:
            self.__tankPanelCtrl.dispose()
            self.__tankPanelCtrl = None
        if self.__abilitiesPanelCtrl:
            self.__abilitiesPanelCtrl.dispose()
            self.__abilitiesPanelCtrl = None
        if self._markersCtrl:
            self._markersCtrl.clear()
            self._markersCtrl = None
        super(GrinchHudView, self)._finalize()
        return

    def _onTurretDeployEvent(self, event):
        with self.viewModel.transaction() as transaction:
            transaction.setTurretLimit(event.slavesLimit)
            transaction.setDeployedTurrets(event.slavesCount)

    def _onTurretStacksUpdatedEvent(self, event):
        with self.viewModel.transaction() as transaction:
            transaction.setTurretsAvailable(event.stacks)
            transaction.setTurretStackReloadTimeLeft(event.reloadTimeLeft)
            transaction.setTurretStackReloadTime(event.reloadTime)

    def _onHomebaseMarkerEvent(self, event):
        with self.viewModel.transaction() as model:
            baseMarkers = model.getBaseMarkers()
            for markerModel in baseMarkers:
                team = markerModel.getTeam()
                if team == event.team:
                    self._markersCtrl.remove(markerModel.proxy)
                    self._markersCtrl.add(markerModel.proxy, event.matrix)

            baseMarkers.invalidate()

    def _onArenaPeriodChange(self, arenaPeriod, _, __, *args):
        self.__setArenaPeriodPanelState(arenaPeriod)

    def __setArenaPeriodPanelState(self, arenaPeriod):
        if arenaPeriod == ARENA_PERIOD.PREBATTLE:
            self.viewModel.setIsGameStarting(True)
        elif arenaPeriod == ARENA_PERIOD.BATTLE:
            self.viewModel.setIsGameStarting(False)

    @MethodsRules.delayable('arenaLoadCompleted')
    def __setup(self):
        self.viewModel.hold()
        self.__initDamageIndicatorModel()
        self.__initTeamScoreModel()
        self.__initHomebaseMarkerModel()
        period = BigWorld.player().arena.period
        self.__setArenaPeriodPanelState(period)
        self.__playersPanelCtrl = PlayersPanelCtrl(weakref.proxy(self), self.__teamGuiOrder)
        self.__tankPanelCtrl = TankPanelCtrl(weakref.proxy(self))
        self.__abilitiesPanelCtrl = AbilitiesPanelCtrl(weakref.proxy(self))
        scoreCmp = getScoreComponent()
        if scoreCmp:
            self.__onTeamScoreUpdated(scoreCmp.teamScore)
            self.__onVehiclePointsUpdated(scoreCmp.vehiclePoints)
        else:
            _logger.warning('[GrinchHudView] Team score component is still None!')
        self.viewModel.commit()

    def __initDamageIndicatorModel(self):
        with self.viewModel.transaction() as model:
            damageIndicators = model.getDamageIndicators()
            damageIndicators.clear()
            damageIndicators.reserve(GrinchHitDamagePull.maxIndicators())
            for _ in xrange(GrinchHitDamagePull.maxIndicators()):
                indicatorModel = GrinchDamageIndicatorModel()
                indicatorModel.setType(DamageIndicatorTypeEnum.NONE)
                damageIndicators.addViewModel(indicatorModel)

            damageIndicators.invalidate()

    def __initTeamScoreModel(self):
        with self.viewModel.transaction() as model:
            teamScoreModels = model.getTeamScore()
            teamScoreModels.clear()
            teamScoreModels.reserve(len(self.__teamGuiOrder))
            for team in self.__teamGuiOrder:
                teamScoreModel = TeamScoreModel()
                teamScoreModel.setTeam(team)
                teamScoreModel.setTeamColor(getTeamColorModelData(team))
                teamScoreModels.addViewModel(teamScoreModel)

            teamScoreModels.invalidate()

    def __initHomebaseMarkerModel(self):
        arenaDP = self.sessionProvider.getArenaDP()
        teams = arenaDP.getAllyTeams() + (Teams.BOTS,)
        teams += tuple((team for team in PLAYER_TEAMS if team not in teams))
        teams = list(reversed(teams))
        with self.viewModel.transaction() as model:
            baseMarkers = model.getBaseMarkers()
            baseMarkers.clear()
            baseMarkers.reserve(len(teams))
            for team in teams:
                markerModel = GrinchMarkerModel()
                markerModel.setTeam(team)
                markerModel.setIsEnemy(arenaDP.isEnemyTeam(team))
                markerModel.setType(getMarkerTypeModelData(team))
                baseMarkers.addViewModel(markerModel)
                self._markersCtrl.add(markerModel.proxy, getHomebaseMarkerTransform(team))

            baseMarkers.invalidate()

    def __onVehicleStateUpdated(self, state, _):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.viewModel.setIsRespawning(True)
        elif state == VEHICLE_VIEW_STATE.SWITCHING:
            self.viewModel.setIsRespawning(False)

    def __onTeamScoreUpdated(self, score):
        scoreLimit = 0
        with self.viewModel.transaction() as model:
            teamScoreModels = model.getTeamScore()
            for teamScoreModel in teamScoreModels:
                team = teamScoreModel.getTeam()
                currentScore, scoreLimit = score.get(team, (teamScoreModel.getScore(), teamScoreModel.getScoreLimit()))
                teamScoreModel.setScore(currentScore)
                teamScoreModel.setScoreLimit(scoreLimit)

            teamScoreModels.invalidate()
            baseMarkers = model.getBaseMarkers()
            for markerModel in baseMarkers:
                team = markerModel.getTeam()
                currentScore, _ = score.get(team, (markerModel.getScore(), 0))
                markerModel.setScore(currentScore)

            baseMarkers.invalidate()
            model.setScoreLimit(scoreLimit)

    def __onVehiclePointsUpdated(self, vehiclePoints):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        for vehicleID, (points, limit) in vehiclePoints.iteritems():
            if vehicleID == playerVehicleID:
                with self.viewModel.transaction() as model:
                    model.setCarryingItems(points)
                    model.setItemsLimit(limit)

    def __teamSortKey(self, item):
        return self.__teamGuiOrder.index(item[0]) if item[0] in self.__teamGuiOrder else -1
