# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/score_panel.py
from gui.Scaleform.daapi.view.meta.EpicScorePanelMeta import EpicScorePanelMeta
import BigWorld
from constants import ARENA_PERIOD
from debug_utils import LOG_ERROR
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.battle_control.controllers.epic_missions_ctrl import PlayerMission

class EpicScorePanel(EpicScorePanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicScorePanel, self).__init__()
        self.__hqMsgSent = False
        self.__nearestHQ = None
        self.__currentTargetID = -1
        self.__currentTargetType = -1
        self.__isInFreeSpectatorMode = False
        self.__isInRespawn = False
        self.__isInHQSector = False
        self.__currentMission = PlayerMission()
        self.__prebattleTimeSent = False
        self.__debugData = {}
        return

    def _populate(self):
        super(EpicScorePanel, self)._populate()
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        destructEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
        if destructEntityComp is not None:
            destructEntityComp.onDestructibleEntityAdded += self.__onDestructibleEntityAdded
            destructEntityComp.onDestructibleEntityHealthChanged += self.__onDestructibleEntityHealthChanged
            hqs = destructEntityComp.destructibleEntities
            if hqs:
                if hqs[hqs.keys()[0]].isActive:
                    self.__onHQBattleStarted()
                destroyedHQs = destructEntityComp.getDestroyedEntityIds()
                for i in range(0, len(destroyedHQs)):
                    self.__onHQDestroyed(destroyedHQs[i])

                for destId, entity in hqs.iteritems():
                    self.as_updateHeadquarterHealthS(destId, entity.health / entity.maxHealth)

        else:
            LOG_ERROR('Expected DestructibleEntityComponent not present!')
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseAdded += self.__onSectorBaseAdded
            sectorBaseComp.onSectorBaseCaptured += self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate += self.__onSectorBasePointsUpdate
            self.as_updateBasesS(sectorBaseComp.getNumCapturedBasesByLane(1), sectorBaseComp.getNumCapturedBasesByLane(2), sectorBaseComp.getNumCapturedBasesByLane(3))
        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        ctrl = self.sessionProvider.dynamic.missions
        ctrl.onPlayerMissionUpdated += self.__onPlayerMissionUpdated
        ctrl.onPlayerMissionReset += self.__onPlayerMissionReset
        ctrl.onNearestObjectiveChanged += self.__onNearestObjectiveChanged
        ctrl.onObjectiveBattleStarted += self.__onHQBattleStarted
        self.__currentMission = ctrl.getCurrentMission()
        ctrl = self.sessionProvider.dynamic.spectator
        if ctrl is not None:
            ctrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
            pmctrl = self.sessionProvider.shared.vehicleState
            if pmctrl is not None:
                if pmctrl.isInPostmortem:
                    self.__onSpectatorModeChanged(ctrl.spectatorViewMode)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onVehicleDeployed += self.__onVehicleDeployed
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibilityChanged
            self.__isInRespawn = ctrl.isRespawnVisible()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
            self.__onArenaPeriodChange(arena.period, arena.periodEndTime, arena.periodLength, arena.periodAdditionalInfo)
        self.__updateTarget()
        return

    def __onSpectatorModeChanged(self, mode):
        if mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.__isInFreeSpectatorMode = True
        else:
            self.__isInFreeSpectatorMode = False
            self.__currentTargetID = -1
            self.__currentTargetType = -1
        self.__updateTarget()

    def __onVehicleDeployed(self):
        self.__isInFreeSpectatorMode = False
        self.__currentTargetID = -1
        self.__currentTargetType = -1
        self.__updateTarget()

    def __onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        self.__isInRespawn = isVisible
        self.__currentTargetID = -1
        self.__currentTargetType = -1
        self.__updateTarget()

    def __onArenaPeriodChange(self, arenaPeriod, endTime, *_):
        if not self.__prebattleTimeSent and arenaPeriod not in (ARENA_PERIOD.IDLE, ARENA_PERIOD.WAITING):
            self.as_setPrebattleTimerS(endTime - BigWorld.serverTime() if arenaPeriod == ARENA_PERIOD.PREBATTLE else 0)
            self.__prebattleTimeSent = True

    def _dispose(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        destructEntityComp = getattr(componentSystem, 'destructibleEntityComponent', None)
        if destructEntityComp is not None:
            destructEntityComp.onDestructibleEntityAdded -= self.__onDestructibleEntityAdded
            destructEntityComp.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityHealthChanged
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseAdded -= self.__onSectorBaseAdded
            sectorBaseComp.onSectorBaseCaptured -= self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate -= self.__onSectorBasePointsUpdate
        ctrl = self.sessionProvider.dynamic.missions
        if ctrl is not None:
            ctrl.onPlayerMissionUpdated -= self.__onPlayerMissionUpdated
            ctrl.onPlayerMissionReset -= self.__onPlayerMissionReset
            ctrl.onNearestObjectiveChanged -= self.__onNearestObjectiveChanged
            ctrl.onObjectiveBattleStarted -= self.__onHQBattleStarted
        ctrl = self.sessionProvider.dynamic.spectator
        if ctrl is not None:
            ctrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onVehicleDeployed -= self.__onVehicleDeployed
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibilityChanged
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        super(EpicScorePanel, self)._dispose()
        return

    def __onHQDestroyed(self, id_):
        self.as_headquarterDestroyedS(id_)

    def __onSectorBasePointsUpdate(self, id_, isPlayerTeam, points, capturingStopped, invadersCount, expectedCaptureTime):
        self.as_updatePointsForBaseS(id_, points)

    def __onDestructibleEntityHealthChanged(self, hqID, newHealth, maxHealth, attackerID, attackReason, hitFlags):
        if newHealth == 0:
            self.__onHQDestroyed(hqID)
        else:
            self.as_updateHeadquarterHealthS(hqID, newHealth / maxHealth)

    def __onDestructibleEntityAdded(self, entity):
        destructEntityComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructEntityComp is not None:
            if entity is not None:
                if entity.health == 0:
                    self.__onHQDestroyed(entity.destructibleEntityID)
                else:
                    self.as_updateHeadquarterHealthS(entity.destructibleEntityID, entity.health / entity.maxHealth)
        else:
            LOG_ERROR('Expected DestructibleEntityComponent not present!')
        if entity.isActive:
            self.__onHQBattleStarted()
        return

    def __onPlayerMissionUpdated(self, mission, _):
        self.__currentMission = mission
        if mission.isEmptyMission():
            self.__removeTarget()
        else:
            self.__updateTarget()

    def __onHQBattleStarted(self):
        if not self.__hqMsgSent:
            self.__hqMsgSent = True

    def __onSectorBaseCaptured(self, id_, isPlayerTeam):
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            self.as_updateBasesS(sectorBaseComp.getNumCapturedBasesByLane(1), sectorBaseComp.getNumCapturedBasesByLane(2), sectorBaseComp.getNumCapturedBasesByLane(3))
        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        return

    def __onSectorBaseAdded(self, sectorBase):
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            self.as_updateBasesS(sectorBaseComp.getNumCapturedBasesByLane(1), sectorBaseComp.getNumCapturedBasesByLane(2), sectorBaseComp.getNumCapturedBasesByLane(3))
        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        return

    def __onNearestObjectiveChanged(self, objID, objDistance):
        if self.__nearestHQ != objID:
            self.__nearestHQ = objID
            self.__updateTarget()

    def __onPlayerMissionReset(self):
        self.__currentMission = PlayerMission()

    def __removeTarget(self):
        self.__currentTargetID = -1
        self.__currentTargetType = -1
        self.as_setTargetS(EPIC_CONSTS.TARGET_NONE, None)
        return

    def __updateTarget(self):
        if self.__isInFreeSpectatorMode or self.__isInRespawn or self.__currentMission.isEmptyMission():
            self.__removeTarget()
            return
        else:
            id_ = None
            type_ = EPIC_CONSTS.TARGET_NONE
            if self.__currentMission.isBaseMission():
                id_ = self.__currentMission.id
                type_ = EPIC_CONSTS.TARGET_BASE
            elif self.__currentMission.isObjectivesMission():
                id_ = self.__nearestHQ
                type_ = EPIC_CONSTS.TARGET_HQ
            if id_ is None:
                self.__removeTarget()
                return
            if id_ != self.__currentTargetID or type_ != self.__currentTargetType:
                self.__currentTargetID = id_
                self.__currentTargetType = type_
                self.as_setTargetS(type_, id_)
            return
