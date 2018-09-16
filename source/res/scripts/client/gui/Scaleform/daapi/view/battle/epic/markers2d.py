# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/markers2d.py
import BigWorld
import GUI
from constants import VEHICLE_HIT_FLAGS
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.battle_control.arena_info.interfaces import IVehiclesAndPositionsController
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from helpers import time_utils
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS
from debug_utils import LOG_ERROR
from Math import Vector3, Matrix, WGTerrainMP, WGClampMP
from arena_component_system.epic_sector_warning_component import WARNING_TYPE
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.game_notification_ctrl import EPIC_NOTIFICATION
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class EpicMarkerPlugin(plugins.MarkerPlugin):

    def _setMarkerSticky(self, handle, active):
        if self._parentObj is not None:
            self._parentObj.setMarkerSticky(handle, active)
        return

    def _setMarkerMinScale(self, handle, minscale):
        if self._parentObj is not None:
            self._parentObj.setMarkerMinScale(handle, minscale)
        return


class EpicMissionsPlugin(EpicMarkerPlugin):
    __slots__ = ('_isInFreeSpectatorMode',)

    def __init__(self, parentObj):
        super(EpicMissionsPlugin, self).__init__(parentObj)
        self._isInFreeSpectatorMode = False

    def start(self):
        super(EpicMissionsPlugin, self).start()
        missionCtrl = self.sessionProvider.dynamic.missions
        if missionCtrl is not None:
            missionCtrl.onPlayerMissionUpdated += self._onPlayerMissionUpdated
            missionCtrl.onPlayerMissionReset += self._onPlayerMissionReset
            missionCtrl.onNearestObjectiveChanged += self._onNearestObjectiveChanged
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self._onSpectatorModeChanged
            pmctrl = self.sessionProvider.shared.vehicleState
            if pmctrl is not None:
                if pmctrl.isInPostmortem:
                    self._onSpectatorModeChanged(specCtrl.spectatorViewMode)
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onVehicleDeployed += self._onVehicleDeployed
        self._onPlayerMissionUpdated(missionCtrl.getCurrentMission(), None)
        return

    def stop(self):
        missionCtrl = self.sessionProvider.dynamic.missions
        if missionCtrl is not None:
            missionCtrl.onPlayerMissionUpdated -= self._onPlayerMissionUpdated
            missionCtrl.onPlayerMissionReset -= self._onPlayerMissionReset
            missionCtrl.onNearestObjectiveChanged -= self._onNearestObjectiveChanged
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged -= self._onSpectatorModeChanged
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onVehicleDeployed -= self._onVehicleDeployed
        super(EpicMissionsPlugin, self).stop()
        return

    def _onPlayerMissionUpdated(self, mission, additionalDescription):
        pass

    def _onPlayerMissionReset(self):
        pass

    def _onNearestObjectiveChanged(self, objID, objDistance):
        pass

    def _onSpectatorModeChanged(self, mode):
        self._isInFreeSpectatorMode = mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM
        self._updateHighlight()

    def _onVehicleDeployed(self):
        self._isInFreeSpectatorMode = False
        self._updateHighlight()

    def _updateHighlight(self):
        pass


class SectorBasesPlugin(EpicMissionsPlugin):
    __slots__ = ('__markers', '__highlightedBaseID', '_isInFreeSpectatorMode', '__basesToBeActive', '__capturedBases', '__insideCircle')

    def __init__(self, parentObj):
        super(SectorBasesPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__highlightedBaseID = -1
        self._isInFreeSpectatorMode = False
        self.__basesToBeActive = []
        self.__capturedBases = []
        self.__insideCircle = -1

    def init(self):
        super(SectorBasesPlugin, self).init()
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseAdded += self.__onSectorBaseAdded
            sectorBaseComp.onSectorBaseCaptured += self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate += self.__onSectorBasePointsUpdate
            sectorBaseComp.onSectorBaseActiveStateChanged += self.__onSectorBaseActiveStateChanged
        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        progressCtrl.onVehicleEntered += self.__onVehicleEntered
        progressCtrl.onVehicleLeft += self.__onVehicleLeft
        return

    def fini(self):
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseAdded -= self.__onSectorBaseAdded
            sectorBaseComp.onSectorBaseCaptured -= self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate -= self.__onSectorBasePointsUpdate
            sectorBaseComp.onSectorBaseActiveStateChanged -= self.__onSectorBaseActiveStateChanged
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        if progressCtrl is not None:
            progressCtrl.onVehicleEntered -= self.__onVehicleEntered
            progressCtrl.onVehicleLeft -= self.__onVehicleLeft
        super(SectorBasesPlugin, self).fini()
        return

    def start(self):
        super(SectorBasesPlugin, self).start()
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBases = sectorBaseComp.sectorBases
            for base in sectorBases:
                inCircle, _ = progressCtrl.getPlayerCircleState(PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE, base.baseID)
                if inCircle:
                    self.__onVehicleEntered(PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE, base.baseID, None)
                self.__onSectorBaseAdded(base)
                if base.capturePercentage > 0:
                    self.__onSectorBasePointsUpdate(base.baseID, base.isPlayerTeam(), base.capturePercentage, base.capturingStopped, 0, '')

        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        return

    def stop(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()
        super(SectorBasesPlugin, self).stop()

    def _onPlayerMissionUpdated(self, mission, _):
        self.__resetBaseHighlight()
        if mission.isBaseMission():
            handle = self.__markers.get(mission.id, None)
            self.__highlightedBaseID = mission.id
            if handle and not self._isInFreeSpectatorMode:
                self._setMarkerSticky(handle, True)
                self._setMarkerActive(handle, True)
                self._invokeMarker(handle, 'setActive', True)
            for baseId, isActive in self.__basesToBeActive:
                handle = self.__markers.get(baseId, None)
                if handle is not None and baseId not in self.__capturedBases:
                    self.__checkPlayerInsideCircle(baseId)
                    self._setMarkerActive(handle, isActive)

            self.__basesToBeActive = []
        return

    def _onPlayerMissionReset(self):
        self.__resetBaseHighlight()

    def _updateHighlight(self):
        handle = self.__markers.get(self.__highlightedBaseID, None)
        if handle:
            self._setMarkerSticky(handle, not self._isInFreeSpectatorMode)
            self._invokeMarker(handle, 'setActive', not self._isInFreeSpectatorMode)
        return

    def __resetBaseHighlight(self):
        handle = self.__markers.get(self.__highlightedBaseID, None)
        if handle:
            self._setMarkerSticky(handle, False)
            self._invokeMarker(handle, 'setActive', False)
            self.__highlightedBaseID = -1
        return

    def __onVehicleEntered(self, type_, idx, state):
        if type_ != PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE:
            return
        else:
            self.__insideCircle = idx
            handle = self.__markers.get(idx, None)
            if handle is not None:
                self._invokeMarker(handle, 'notifyVehicleInCircle', True)
            return

    def __onVehicleLeft(self, type_, idx):
        if type_ != PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE:
            return
        else:
            handle = self.__markers.get(idx, None)
            if handle is not None:
                self.__insideCircle = -1
                self._invokeMarker(handle, 'notifyVehicleInCircle', False)
            return

    def __onSectorBaseAdded(self, sectorBase):
        handle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.SECTOR_BASE_TYPE, sectorBase.position + settings.MARKER_POSITION_ADJUSTMENT)
        if handle is None:
            return
        else:
            self._setMarkerSticky(handle, False)
            self._setMarkerActive(handle, sectorBase.active())
            self._setMarkerMinScale(handle, 100)
            self._invokeMarker(handle, 'setOwningTeam', sectorBase.isPlayerTeam())
            self._invokeMarker(handle, 'setIdentifier', sectorBase.baseID)
            self._invokeMarker(handle, 'setActive', False)
            self.__markers[sectorBase.baseID] = handle
            self.__checkPlayerInsideCircle(sectorBase.baseID)
            return

    def __onSectorBaseCaptured(self, baseId, isPlayerTeam):
        handle = self.__markers.get(baseId)
        if handle is not None:
            self._invokeMarker(handle, 'setOwningTeam', isPlayerTeam)
            self.__capturedBases.append(baseId)
        if baseId == self.__highlightedBaseID:
            self._invokeMarker(handle, 'setActive', False)
            self._setMarkerSticky(handle, False)
            self.__highlightedBaseID = -1
        return

    def __onSectorBasePointsUpdate(self, baseId, isPlayerTeam, points, capturingStopped, invadersCount, expectedCaptureTime):
        handle = self.__markers.get(baseId)
        if handle is not None:
            self._invokeMarker(handle, 'setCapturePoints', points)
        return

    def __onSectorBaseActiveStateChanged(self, baseId, isActive):
        handle = self.__markers.get(baseId, None)
        if handle is not None:
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
            if sectorBaseComp is None:
                LOG_ERROR('Expected SectorBaseComponent not present!')
                return
            baseLane = sectorBaseComp.getSectorForSectorBase(baseId).playerGroup
            playerData = getattr(componentSystem, 'playerDataComponent', None)
            if playerData is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
            if isActive and baseLane == playerData.physicalLane:
                self.__basesToBeActive.append((baseId, isActive))
            else:
                self.__checkPlayerInsideCircle(baseId)
                self._setMarkerActive(handle, isActive)
        return

    def __checkPlayerInsideCircle(self, baseId):
        handle = self.__markers.get(baseId, None)
        if handle:
            self._invokeMarker(handle, 'notifyVehicleInCircle', self.__insideCircle == baseId)
        return


class HeadquartersPlugin(EpicMissionsPlugin):
    __slots__ = ('__markers', '__isHQBattle', '__visibleHQ', '_isInFreeSpectatorMode', '__hqMissionActive')

    def __init__(self, parentObj):
        super(HeadquartersPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__isHQBattle = False
        self.__visibleHQ = -1
        self._isInFreeSpectatorMode = False
        self.__hqMissionActive = False

    def init(self):
        super(HeadquartersPlugin, self).init()
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded += self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityStateChanged += self.__onDestructibleEntityStateChanged
            destructibleComponent.onDestructibleEntityHealthChanged += self.__onDestructibleEntityHealthChanged
        else:
            LOG_ERROR('Expected DestructibleEntityComponent not present!')
        return

    def fini(self):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded -= self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityStateChanged -= self.__onDestructibleEntityStateChanged
            destructibleComponent.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityHealthChanged
        super(HeadquartersPlugin, self).fini()
        return

    def start(self):
        super(HeadquartersPlugin, self).start()
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            hqs = destructibleComponent.destructibleEntities
            for hq in hqs.itervalues():
                self.__onDestructibleEntityAdded(hq)

        else:
            LOG_ERROR('Expected DestructibleEntityComponent not present!')
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()
        super(HeadquartersPlugin, self).stop()
        return

    def resetHQHighlight(self):
        handle = self.__markers.get(self.__visibleHQ, None)
        if handle:
            self._setMarkerSticky(handle, False)
            self._invokeMarker(handle, 'setHighlight', False)
            self.__visibleHQ = -1
        return

    def _onPlayerMissionUpdated(self, mission, _):
        if not mission.isObjectivesMission():
            self.resetHQHighlight()
            self.__hqMissionActive = False
        else:
            self.__startHQBattle()
            self.__hqMissionActive = True
            ctrl = self.sessionProvider.dynamic.missions
            objID, objDis = ctrl.getNearestObjectiveData()
            self._onNearestObjectiveChanged(objID, objDis)

    def _onPlayerMissionReset(self):
        self.resetHQHighlight()

    def _onNearestObjectiveChanged(self, objID, _):
        if self.__hqMissionActive:
            self.resetHQHighlight()
            self.__visibleHQ = objID
            handle = self.__markers.get(objID, None)
            if handle and not self._isInFreeSpectatorMode:
                self._setMarkerSticky(handle, True)
                self._invokeMarker(handle, 'setHighlight', True)
        return

    def _updateHighlight(self):
        handle = self.__markers.get(self.__visibleHQ, None)
        if handle:
            self._setMarkerSticky(handle, not self._isInFreeSpectatorMode)
            self._invokeMarker(handle, 'setHighlight', not self._isInFreeSpectatorMode)
        return

    def __startHQBattle(self):
        if self.__isHQBattle:
            return
        else:
            self.__isHQBattle = True
            destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is not None:
                hqs = destructibleComponent.destructibleEntities
                for hqId, _ in hqs.iteritems():
                    self.__activateDestructibleMarker(hqId, True)

            else:
                LOG_ERROR('Expected DestructibleEntityComponent not present!')
            return

    def __onDestructibleEntityAdded(self, entity):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is None:
            LOG_ERROR('Expected DestructibleEntityComponent not present!')
            return
        elif entity is None:
            LOG_ERROR('Expected DestructibleEntity not present!')
            return
        else:
            handle = self._createMarkerWithMatrix(settings.MARKER_SYMBOL_NAME.HEADQUARTER_TYPE, self.__getMarkerMatrix(entity))
            if handle is None:
                return
            isDead = False
            if entity.health <= 0:
                isDead = True
            self._setMarkerActive(handle, entity.isActive)
            self._setMarkerMinScale(handle, 100)
            self._invokeMarker(handle, 'setOwningTeam', entity.isPlayerTeam)
            self._invokeMarker(handle, 'setDead', isDead)
            self._invokeMarker(handle, 'setIdentifier', entity.destructibleEntityID)
            self._invokeMarker(handle, 'setMaxHealth', entity.maxHealth)
            self._invokeMarker(handle, 'setHealth', int(entity.health))
            self.__markers[entity.destructibleEntityID] = handle
            if entity.destructibleEntityID == self.__visibleHQ:
                self._onNearestObjectiveChanged(entity.destructibleEntityID, None)
            else:
                self._setMarkerSticky(handle, False)
                self._invokeMarker(handle, 'setHighlight', False)
            return

    def __onDestructibleEntityStateChanged(self, entityId):
        handle = self.__markers.get(entityId, None)
        if handle:
            destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is None:
                LOG_ERROR('Expected DestructibleEntityComponent not present!')
                return
            hq = destructibleComponent.getDestructibleEntity(entityId)
            if hq is None:
                LOG_ERROR('Expected DestructibleEntity not present! Id: ' + str(entityId))
                return
            self._setMarkerMatrix(handle, self.__getMarkerMatrix(hq))
            if not hq.isAlive():
                self._invokeMarker(handle, 'setHealth', 0)
                self._invokeMarker(handle, 'setDead', True)
                self._setMarkerSticky(handle, False)
        return

    def __getMarkerMatrix(self, destructibleEntity):
        guiNode = destructibleEntity.getGuiNode()
        if guiNode is not None:
            return guiNode
        else:
            m = Matrix()
            m.translation = destructibleEntity.position + settings.MARKER_POSITION_ADJUSTMENT
            return m

    def __onDestructibleEntityHealthChanged(self, entityId, newHealth, maxHealth, attackerID, attackReason, hitFlags):
        handle = self.__markers.get(entityId, None)
        aInfo = self.sessionProvider.getArenaDP().getVehicleInfo(attackerID)
        vehDmg = self.__getVehicleDamageType(aInfo)
        self._invokeMarker(handle, 'setHealth', newHealth, vehDmg, hitFlags & VEHICLE_HIT_FLAGS.IS_ANY_PIERCING_MASK)
        return

    def __activateDestructibleMarker(self, entityId, isActive):
        handle = self.__markers.get(entityId, None)
        if handle is not None:
            self._setMarkerActive(handle, isActive)
        return

    def __getVehicleDamageType(self, attackerInfo):
        if not attackerInfo:
            return settings.DAMAGE_TYPE.FROM_UNKNOWN
        attackerID = attackerInfo.vehicleID
        if attackerID == BigWorld.player().playerVehicleID:
            return settings.DAMAGE_TYPE.FROM_PLAYER
        entityName = self.sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        if entityName == PLAYER_GUI_PROPS.squadman:
            return settings.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_GUI_PROPS.ally:
            return settings.DAMAGE_TYPE.FROM_ALLY
        return settings.DAMAGE_TYPE.FROM_ENEMY if entityName == PLAYER_GUI_PROPS.enemy else settings.DAMAGE_TYPE.FROM_UNKNOWN

    def __onMinimapFeedbackReceived(self, eventID, entityID, value):
        if eventID == FEEDBACK_EVENT_ID.MINIMAP_MARK_OBJECTIVE:
            self.__doAttentionToObjective(entityID, *value)

    def __doAttentionToObjective(self, senderID, hqId, duration):
        handle = self.__markers.get(hqId, None)
        if handle:
            self._invokeMarker(handle, 'setTarget')
        return


class StepRepairPointPlugin(EpicMarkerPlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(StepRepairPointPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(StepRepairPointPlugin, self).init()
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded += self.__onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged += self.__onStepRepairPointActiveStateChanged
        else:
            LOG_ERROR('Expected StepRepairPointComponent not present!')
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        if progressCtrl is not None:
            progressCtrl.onTimerUpdated += self.__onTimerUpdated
            progressCtrl.onCircleStatusChanged += self.__onCircleStatusChanged
            progressCtrl.onVehicleEntered += self.__onVehicleEntered
            progressCtrl.onVehicleLeft += self.__onVehicleLeft
        return

    def fini(self):
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded -= self.__onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged -= self.__onStepRepairPointActiveStateChanged
        ctrl = self.sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onTimerUpdated -= self.__onTimerUpdated
            ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
            ctrl.onVehicleEntered -= self.__onVehicleEntered
            ctrl.onVehicleLeft -= self.__onVehicleLeft
        super(StepRepairPointPlugin, self).fini()
        return

    def start(self):
        super(StepRepairPointPlugin, self).start()
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            repairPts = stepRepairPointComponent.stepRepairPoints
            for pt in repairPts:
                self.__onStepRepairPointAdded(pt)
                inCircle, state = progressCtrl.getPlayerCircleState(PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE, pt.id)
                if inCircle:
                    self.__onVehicleEntered(PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE, pt.id, state)

        else:
            LOG_ERROR('Expected StepRepairPointComponent not present!')
        return

    def stop(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()
        super(StepRepairPointPlugin, self).stop()

    def __onVehicleEntered(self, type_, idx, state):
        if type_ != PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        else:
            handle = self.__markers[idx]
            if handle is not None:
                self._invokeMarker(handle, 'notifyVehicleInCircle', True)
                self._parentObj.invokeMarker(handle, 'setState', [state])
            return

    def __onVehicleLeft(self, type_, idx):
        if type_ != PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        else:
            handle = self.__markers[idx]
            if handle is not None:
                self._invokeMarker(handle, 'notifyVehicleInCircle', False)
            return

    def __onTimerUpdated(self, type_, pointId, timeLeft):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        handle = self.__markers[pointId]
        self._parentObj.invokeMarker(handle, 'setCooldown', [time_utils.getTimeLeftFormat(timeLeft)])

    def __onCircleStatusChanged(self, type_, pointId, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        handle = self.__markers[pointId]
        self._parentObj.invokeMarker(handle, 'setState', [state])

    def __onStepRepairPointAdded(self, stepRepairPoint):
        handle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.STEP_REPAIR_MARKER_TYPE, stepRepairPoint.position + settings.MARKER_POSITION_ADJUSTMENT)
        if handle is None:
            return
        else:
            self._setMarkerActive(handle, stepRepairPoint.isActiveForPlayerTeam())
            self._setMarkerMinScale(handle, 40)
            self.__markers[stepRepairPoint.id] = handle
            return

    def __onStepRepairPointActiveStateChanged(self, pointId, isActive):
        handle = self.__markers[pointId]
        if handle is not None:
            self._setMarkerActive(handle, isActive)
        return


class SectorWarningPlugin(EpicMarkerPlugin):
    WARNING_ID_TO_MARKER_TYPE = {WARNING_TYPE.PROTECTED: EPIC_CONSTS.PROTECTION_ZONE_WARNING,
     WARNING_TYPE.BOMBING: EPIC_CONSTS.BOMBING_WARNING}
    X_DIR = 0
    Y_DIR = 1
    Z_DIR = 2
    MARKER_Y_OFFSET = 10

    class WarningMarker(object):

        def __init__(self):
            self.markerID = None
            self.motor = None
            self.target = None
            return

    def __init__(self, parentObj):
        super(SectorWarningPlugin, self).__init__(parentObj)
        self.__markers = dict()

    def init(self):
        super(SectorWarningPlugin, self).init()
        sectorWarningComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorWarningComponent', None)
        if sectorWarningComponent is not None:
            sectorWarningComponent.onShowSectorWarning += self.__onShowSectorWarning
            sectorWarningComponent.onTransitionTimerUpdated += self.__onTransitionTimerUpdated
        else:
            LOG_ERROR('Expected SectorWarningComponent not present!')
        return

    def start(self):
        super(SectorWarningPlugin, self).start()
        sectorWarningComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorWarningComponent', None)
        if sectorWarningComponent is not None:
            if sectorWarningComponent.warnings is not None:
                for edgeID, warning in sectorWarningComponent.warnings.iteritems():
                    self.__onShowSectorWarning(edgeID, warning.type, warning.targetSectorGroup)

        else:
            LOG_ERROR('Expected SectorWarningComponent not present!')
        return

    def stop(self):
        sectorWarningComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorWarningComponent', None)
        if sectorWarningComponent:
            sectorWarningComponent.onShowSectorWarning -= self.__onShowSectorWarning
            sectorWarningComponent.onTransitionTimerUpdated -= self.__onTransitionTimerUpdated
        super(SectorWarningPlugin, self).stop()
        return

    def __onTransitionTimerUpdated(self, sectorGroupID, seconds):
        sc = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorComponent', None)
        if sc is None:
            LOG_ERROR('Expected SectorComponent not present!')
            return
        else:
            isAttacker = avatar_getter.getPlayerTeam() == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER
            for marker in self.__markers.values():
                targetSectorGroup = sc.getSectorGroupById(marker.target)
                if isAttacker:
                    for targetSector in targetSectorGroup.sectors:
                        timerSectorId = sc.playerGroups[targetSector.playerGroup].sectors.get(targetSector.IDInPlayerGroup - 1, None)
                        if timerSectorId is not None and sc.getSectorById(timerSectorId).groupID == sectorGroupID:
                            self.__updateTimer(marker, seconds)

                if marker.target == sectorGroupID:
                    self.__updateTimer(marker, seconds)

            return

    def __updateTimer(self, marker, seconds):
        if seconds > 0:
            timeStr = time_utils.getTimeLeftFormat(seconds)
            self._invokeMarker(marker.markerID, 'setCountdown', timeStr)
        else:
            self._invokeMarker(marker.markerID, 'clearCountdown')

    def __onShowSectorWarning(self, edgeID, warningID, targetSectorGroupID):
        sectorWarningComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorWarningComponent', None)
        if sectorWarningComponent is None:
            LOG_ERROR('Expected SectorWarningComponent not present!')
            return
        elif None in (edgeID, warningID, targetSectorGroupID):
            LOG_ERROR('[SectorWarningPlugin] Wrong argument!')
            return
        elif warningID in (WARNING_TYPE.NONE, WARNING_TYPE.SAFE):
            if edgeID in self.__markers:
                self._destroyMarker(self.__markers[edgeID].markerID)
                del self.__markers[edgeID]
            return
        else:
            if edgeID in self.__markers:
                marker = self.__markers[edgeID]
                marker.target = targetSectorGroupID
            else:
                marker = self.WarningMarker()
                marker.target = targetSectorGroupID
                edge = sectorWarningComponent.getEdgeByID(edgeID)
                edgeStart, edgeEnd = edge.getEdgePoints()
                direction = self.X_DIR if edgeStart[2] == edgeEnd[2] else self.Z_DIR
                marker.motor = BigWorld.Servo(self.__generateMatrix(direction, edgeStart, edgeEnd))
                marker.markerID = self._createMarkerWithMatrix(settings.MARKER_SYMBOL_NAME.SECTOR_WARNING_MARKER, marker.motor.signal)
                self.__markers[edgeID] = marker
                self._setMarkerSticky(marker.markerID, False)
                self._setMarkerMinScale(marker.markerID, 40)
            markerType = self.WARNING_ID_TO_MARKER_TYPE[warningID]
            self._invokeMarker(marker.markerID, 'showWarning', markerType)
            return

    def __generateMatrix(self, direction, edgeStart, edgeEnd):
        clampMatrix = WGClampMP()
        clampMatrix.source = BigWorld.player().getOwnVehicleMatrix()
        terrainMp = WGTerrainMP(BigWorld.player().spaceID, self.MARKER_Y_OFFSET)
        terrainMp.source = clampMatrix
        if direction == self.X_DIR:
            clampMatrix.max = Vector3(max(edgeStart[0], edgeEnd[0]), 10000, edgeStart[2])
            clampMatrix.min = Vector3(min(edgeStart[0], edgeEnd[0]), -10000, edgeStart[2])
        elif direction == self.Z_DIR:
            clampMatrix.max = Vector3(edgeStart[0], 10000, max(edgeStart[2], edgeEnd[2]))
            clampMatrix.min = Vector3(edgeStart[0], -10000, min(edgeStart[2], edgeEnd[2]))
        return terrainMp


class SectorWaypointsPlugin(EpicMarkerPlugin, IVehiclesAndPositionsController):
    __slots__ = ('__markers', '__currentWaypointSector', '__markerActiveState', '__suspendedForLane', '__currentWaypointPositon', '__marker', '__timeCB', '__currentEndTime', '__suspendedForBase', '__shownWaypoints')

    def __init__(self, parentObj):
        super(SectorWaypointsPlugin, self).__init__(parentObj)
        self.__marker = None
        self.__currentWaypointSector = None
        self.__currentWaypointPositon = None
        self.__markerActiveState = True
        self.__suspendedForBase = None
        self.__suspendedForLane = None
        self.__shownWaypoints = []
        return

    def init(self):
        super(SectorWaypointsPlugin, self).init()
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        component = getattr(componentSystem, 'sectorBaseComponent', None)
        if component is not None:
            component.onSectorBaseCaptured += self.__onSectorBaseCaptured
        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        component = getattr(componentSystem, 'sectorComponent', None)
        if component is not None:
            component.onWaypointsForPlayerActivated += self.__onWaypointsForPlayerActivated
        else:
            LOG_ERROR('Expected SectorComponent not present!')
        component = getattr(componentSystem, 'sectorWarningComponent', None)
        if component is not None:
            componentSystem.sectorWarningComponent.onTransitionTimerUpdated += self.__onTransitionTimerUpdated
        else:
            LOG_ERROR('Expected SectorWarningComponent not present!')
        ctrl = self.sessionProvider.dynamic.gameNotifications
        ctrl.onGameNotificationRecieved += self.__onGameNotificationRecieved
        return

    def fini(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        component = getattr(componentSystem, 'sectorBaseComponent', None)
        if component is not None:
            component.onSectorBaseCaptured -= self.__onSectorBaseCaptured
        component = getattr(componentSystem, 'sectorComponent', None)
        if component is not None:
            component.onWaypointsForPlayerActivated -= self.__onWaypointsForPlayerActivated
        component = getattr(componentSystem, 'sectorWarningComponent', None)
        if component is not None:
            componentSystem.sectorWarningComponent.onTransitionTimerUpdated -= self.__onTransitionTimerUpdated
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl is not None:
            ctrl.onGameNotificationRecieved -= self.__onGameNotificationRecieved
        super(SectorWaypointsPlugin, self).fini()
        return

    def start(self):
        super(SectorWaypointsPlugin, self).start()
        sectorComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorComponent', None)
        if sectorComponent is not None:
            waypointSectorTimeTuple = sectorComponent.getActiveWaypointSectorGroupForPlayer()
            if waypointSectorTimeTuple[0] is not None:
                self.__onWaypointsForPlayerActivated(waypointSectorTimeTuple)
        else:
            LOG_ERROR('Expected SectorComponent not present!')
        self.sessionProvider.addArenaCtrl(self)
        return

    def stop(self):
        self.sessionProvider.removeArenaCtrl(self)
        if self.__marker is not None:
            self._destroyMarker(self.__marker)
        super(SectorWaypointsPlugin, self).stop()
        return

    def updatePositions(self, iterator):
        if not self.__marker or not self.__currentWaypointSector:
            return
        else:
            sectorComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorComponent', None)
            if sectorComponent is None:
                LOG_ERROR('Expected SectorComponent not present!')
                return
            waypointPosition = sectorComponent.getClosestWayPointForSectorAndTeam(self.__currentWaypointSector.sectorID, self.sessionProvider.arenaVisitor.type, avatar_getter.getPlayerTeam(), avatar_getter.getOwnVehiclePosition())
            if waypointPosition is None:
                return
            if waypointPosition != self.__currentWaypointPositon:
                self.__currentWaypointPositon = waypointPosition
                self._setMarkerPosition(self.__marker, self.__currentWaypointPositon + settings.MARKER_POSITION_ADJUSTMENT)
            return

    def __onGameNotificationRecieved(self, notificationType, data):
        if notificationType != EPIC_NOTIFICATION.ZONE_CAPTURED:
            return
        else:
            if self.__suspendedForBase == data['id']:
                currentSuspensionLane = self.__suspendedForLane
                self.__suspendedForBase = None
                self.__suspendedForLane = None
                if self.__currentWaypointSector is not None:
                    playerData = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
                    if playerData is None:
                        LOG_ERROR('Expected PlayerDataComponent not present!')
                        return
                    if currentSuspensionLane == playerData.physicalLane:
                        self.__markerActiveState = True
                        if self.__marker is not None and self.__currentWaypointPositon is not None:
                            self._setMarkerActive(self.__marker, self.__markerActiveState)
            return

    def __onWaypointsForPlayerActivated(self, waypointSectorTimeTuple):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        sectorComponent = getattr(componentSystem, 'sectorComponent', None)
        if sectorComponent is None:
            LOG_ERROR('Expected SectorComponent not present!')
            return
        else:
            playerData = getattr(componentSystem, 'playerDataComponent', None)
            if playerData is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            sectorGroup, sectorID, _ = waypointSectorTimeTuple
            if not self.__marker:
                self.__marker = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.WAYPOINT_MARKER, (0, 0, 0))
                self._invokeMarker(self.__marker, 'isAttacker', False)
                self._setMarkerActive(self.__marker, False)
            if sectorGroup and sectorID:
                if sectorID in self.__shownWaypoints:
                    self.__currentWaypointSector = None
                    return
                self.__shownWaypoints.append(sectorID)
                self.__currentWaypointSector = sectorComponent.getSectorById(sectorID)
            else:
                self.__currentWaypointSector = None
            if sectorGroup is None and self.__marker is not None:
                self.__markerActiveState = False
                self._setMarkerActive(self.__marker, self.__markerActiveState)
                return
            if sectorGroup is None:
                return
            if self.__suspendedForLane != playerData.physicalLane or self.__suspendedForLane is None:
                self.__suspendedForBase = None
                self.__suspendedForLane = None
                self.__markerActiveState = True
            else:
                self.__markerActiveState = False
            self.__currentWaypointPositon = sectorComponent.getClosestWayPointForSectorAndTeam(sectorID, self.sessionProvider.arenaVisitor.getArenaType(), avatar_getter.getPlayerTeam(), BigWorld.player().position)
            if self.__currentWaypointPositon is None:
                self.__markerActiveState = False
                self._setMarkerActive(self.__marker, self.__markerActiveState)
                return
            self._setMarkerPosition(self.__marker, self.__currentWaypointPositon + settings.MARKER_POSITION_ADJUSTMENT)
            self._setMarkerActive(self.__marker, self.__markerActiveState)
            self._setMarkerSticky(self.__marker, True)
            self._setMarkerMinScale(self.__marker, 100)
            return

    def __onTransitionTimerUpdated(self, sectorGroupID, seconds):
        if self.__markerActiveState and self.__currentWaypointSector and self.__currentWaypointSector.groupID == sectorGroupID and self.__marker:
            if seconds >= 0:
                timeStr = time_utils.getTimeLeftFormat(seconds)
                self._invokeMarker(self.__marker, 'setCountdown', timeStr)
            else:
                self._invokeMarker(self.__marker, 'clearCountdown')

    def __onSectorBaseCaptured(self, baseId, isPlayerTeam):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            playerData = getattr(componentSystem, 'playerDataComponent', None)
            if playerData is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            baseLane = sectorBaseComp.getSectorForSectorBase(baseId).playerGroup
            if baseLane == playerData.physicalLane:
                self.__suspendedForBase = baseId
                self.__suspendedForLane = baseLane
            return


class EpicMarkersManager(MarkersManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _createCanvas(self, arenaVisitor):
        return GUI.WGVehicleStickyMarkersCanvasFlashAS3(self.movie)

    def _setupPlugins(self, arenaVisitor):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.__onRespawnScreenVisibilityChanged
        setup = super(EpicMarkersManager, self)._setupPlugins(arenaVisitor)
        if arenaVisitor.hasSectors():
            setup['sector_bases'] = SectorBasesPlugin
            if avatar_getter.getPlayerTeam() == EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER:
                setup['sector_waypoints'] = SectorWaypointsPlugin
            setup['sector_warnings'] = SectorWarningPlugin
        if arenaVisitor.hasDestructibleEntities():
            setup['hq'] = HeadquartersPlugin
        if arenaVisitor.hasStepRepairPoints():
            setup['step_repairs'] = StepRepairPointPlugin
        return setup

    def stopPlugins(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnScreenVisibilityChanged
        super(EpicMarkersManager, self).stopPlugins()
        return

    def __onRespawnScreenVisibilityChanged(self, isRespawnScreenVisible):
        self.setVisible(not isRespawnScreenVisible)
