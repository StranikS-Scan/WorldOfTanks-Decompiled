# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/markers2d.py
import logging
import BigWorld
from Math import Vector3, Vector4, Matrix, WGTerrainMP, WGClampMP, Vector2
from arena_component_system.epic_sector_warning_component import WARNING_TYPE
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, INVALID_MARKER_ID, INVALID_MARKER_SUBTYPE, MarkerType, DefaultMarkerSubType, INVALID_TARGET_ID, INVALID_COMMAND_ID
from constants import VEHICLE_HIT_FLAGS
from debug_utils import LOG_ERROR
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager, markers
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import BaseMarker
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import ChatCommunicationComponent, ReplyStateForMarker
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IVehiclesAndPositionsController
from gui.battle_control.battle_constants import ENTITY_IN_FOCUS_TYPE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE
from gui.battle_control.controllers.feedback_adaptor import EntityInFocusData
from gui.battle_control.controllers.game_notification_ctrl import EPIC_NOTIFICATION
from helpers import dependency
from helpers import time_utils
from messenger.proto.bw_chat2.battle_chat_cmd import BASE_CMD_NAMES, AUTOCOMMIT_COMMAND_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.gui.battle_session import IBattleSessionProvider
_SECTOR_BASES_BOUNDS_MIN_SCALE = Vector2(1.0, 1.0)
_SECTOR_BASES_BOUNDS = Vector4(30, 30, 30, 30)
_INNER_SECTOR_BASES_BOUNDS = Vector4(17, 17, 18, 18)
_HEADQUARTERS_BOUNDS_MIN_SCALE = Vector2(1.0, 0.8)
_HEADQUARTERS_BOUNDS = Vector4(50, 50, 30, 65)
_INNER_HEADQUARTERS_BOUNDS = Vector4(17, 17, 18, 25)
_MEDIUM_MARKER_MIN_SCALE = 100
_EMPTY_MARKER_BOUNDS = Vector4(0.0, 0.0, 0.0, 0.0)
_EMPTY_MARKER_INNER_BOUNDS = Vector4(0.0, 0.0, 0.0, 0.0)
_MAX_CULL_DISTANCE = 1000000.0
_SMALL_MARKER_MIN_SCALE = 40
_NEAR_MARKER_CULL_DISTANCE = 300
_EPIC_BASE = 'epic_base'
_ALLY_OWNER = 'ally'
_ENEMY_OWNER = 'enemy'
_logger = logging.getLogger(__name__)

class EpicMissionsPlugin(plugins.MarkerPlugin):
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

    @staticmethod
    def _getAnyMarkerRepliedByPlayer(markerList):
        somethingRepliedByMe = False
        for marker in markerList.itervalues():
            if marker.getIsRepliedByPlayer():
                somethingRepliedByMe = True
                break

        return somethingRepliedByMe


class SectorBasesPlugin(EpicMissionsPlugin, ChatCommunicationComponent):
    _AUTO_COMMIT_STATE_TO_STATE = {BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE: BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
     BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE: BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE}
    __slots__ = ('_markers', '__highlightedBaseID', '_isInFreeSpectatorMode', '__basesToBeActive', '__capturedBases', '__insideCircle', '__clazz')

    def __init__(self, parentObj, clazz=markers.BaseMarker):
        super(SectorBasesPlugin, self).__init__(parentObj)
        self._markers = {}
        self.__clazz = clazz
        self.__highlightedBaseID = INVALID_TARGET_ID
        self._isInFreeSpectatorMode = False
        self.__basesToBeActive = []
        self.__capturedBases = []
        self.__insideCircle = INVALID_TARGET_ID
        self.__firstSticky = True
        ChatCommunicationComponent.__init__(self, parentObj)

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
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer += self.__setInFocusForPlayer
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
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
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer -= self.__setInFocusForPlayer
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
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
                self.__onSectorBaseAdded(base, isInBase=inCircle)
                if base.capturePercentage > 0:
                    self.__onSectorBasePointsUpdate(base.baseID, base.isPlayerTeam(), base.capturePercentage, base.capturingStopped, 0, '')

        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        ChatCommunicationComponent.start(self)
        return

    def stop(self):
        for marker in self._markers.values():
            self._destroyMarker(marker.getMarkerID())

        self._markers.clear()
        ChatCommunicationComponent.stop(self)
        super(SectorBasesPlugin, self).stop()

    def getMarkerType(self):
        return MarkerType.BASE_MARKER_TYPE

    def getTargetIDFromMarkerID(self, markerID):
        for targetID in self._markers:
            if self._markers[targetID].getMarkerID() == markerID:
                return targetID

        return INVALID_TARGET_ID

    def getMarkerSubtype(self, targetID):
        if targetID == INVALID_TARGET_ID or targetID not in self._markers:
            return INVALID_MARKER_SUBTYPE
        return DefaultMarkerSubType.ALLY_MARKER_SUBTYPE if _ALLY_OWNER == self._markers[targetID].getOwningTeam() else DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE

    def _onPlayerMissionUpdated(self, mission, _):
        self.__resetBaseHighlight()
        if mission.isBaseMission():
            markerID = None
            if mission.id in self._markers:
                markerID = self._markers[mission.id].getMarkerID()
            self.__highlightedBaseID = mission.id
            if markerID is not None and not self._isInFreeSpectatorMode:
                if not EpicMissionsPlugin._getAnyMarkerRepliedByPlayer(self._markers):
                    self._setMarkerSticky(markerID, True)
                self._setMarkerActive(markerID, True)
                self._invokeMarker(markerID, 'setActive', True)
            for baseId, isActive in self.__basesToBeActive:
                markerID = None
                if baseId in self._markers:
                    markerID = self._markers[baseId].getMarkerID()
                if markerID is not None and baseId not in self.__capturedBases:
                    self.__checkPlayerInsideCircle(baseId)
                    self._setMarkerActive(markerID, isActive)

            self.__basesToBeActive = []
        return

    def _onPlayerMissionReset(self):
        self.__resetBaseHighlight()

    def _updateHighlight(self):
        markerID = None
        if self.__highlightedBaseID in self._markers:
            markerID = self._markers[self.__highlightedBaseID].getMarkerID()
        if markerID is not None:
            self._setMarkerSticky(markerID, not self._isInFreeSpectatorMode)
            self._invokeMarker(markerID, 'setActive', not self._isInFreeSpectatorMode)
        return

    def _getMarkerFromTargetID(self, targetID, markerType):
        return None if targetID not in self._markers or markerType != self.getMarkerType() else self._markers[targetID]

    def __onActionAddedToMarkerReceived(self, senderID, commandID, markerType, uniqueBaseID):
        if markerType != self.getMarkerType() or uniqueBaseID not in self._markers or _ACTIONS.battleChatCommandFromActionID(commandID).name not in BASE_CMD_NAMES:
            return
        marker = self._markers[uniqueBaseID]
        marker.setState(ReplyStateForMarker.CREATE_STATE)
        marker.setActiveCommandID(commandID)
        if _ACTIONS.battleChatCommandFromActionID(commandID).name in self._AUTO_COMMIT_STATE_TO_STATE:
            self._setMarkerRepliesAndCheckState(marker, 1, senderID == avatar_getter.getPlayerVehicleID())
        else:
            self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
        if not avatar_getter.isVehicleAlive() and marker.getBoundCheckEnabled():
            marker.setBoundCheckEnabled(False)
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)

    def __setInFocusForPlayer(self, oldTargetID, oldTargetType, newTargetID, newTargetType, oneShot):
        if oldTargetType == self.getMarkerType() and oldTargetID in self._markers:
            self.__makeMarkerSticky(oldTargetID, False)
        if newTargetType == self.getMarkerType() and newTargetID in self._markers:
            self.__makeMarkerSticky(newTargetID, True)
        if oneShot:
            return
        if newTargetID == INVALID_TARGET_ID and self.__highlightedBaseID != INVALID_TARGET_ID:
            self.__makeMarkerSticky(self.__highlightedBaseID, True)
        elif newTargetID != INVALID_TARGET_ID and self.__highlightedBaseID != INVALID_TARGET_ID and newTargetID != self.__highlightedBaseID:
            self.__makeMarkerSticky(self.__highlightedBaseID, False)

    def __makeMarkerSticky(self, targetID, setSticky):
        marker = self._markers[targetID]
        markerID = marker.getMarkerID()
        self._setMarkerSticky(markerID, setSticky)
        marker.setIsSticky(setSticky)
        self._checkNextState(marker)

    def __onRemoveCommandReceived(self, removeID, markerType):
        if markerType != MarkerType.BASE_MARKER_TYPE or removeID not in self._markers:
            return
        marker = self._markers[removeID]
        marker.setActiveCommandID(INVALID_COMMAND_ID)
        self._checkNextState(marker)
        if marker.getState() == ReplyStateForMarker.NO_ACTION and not marker.getBoundCheckEnabled():
            marker.setBoundCheckEnabled(True)
            self._setMarkerBoundEnabled(marker.getMarkerID(), True)

    def __resetBaseHighlight(self):
        marker = None
        if self.__highlightedBaseID in self._markers:
            marker = self._markers[self.__highlightedBaseID]
        if marker is not None:
            markerID = marker.getMarkerID()
            if not marker.getIsRepliedByPlayer():
                self._setMarkerSticky(markerID, False)
            self._invokeMarker(markerID, 'setActive', False)
            self.__highlightedBaseID = INVALID_TARGET_ID
        return

    def __onVehicleEntered(self, type_, idx, state):
        if type_ != PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE:
            return
        else:
            self.__insideCircle = idx
            markerID = None
            if idx in self._markers:
                markerID = self._markers[idx].getMarkerID()
            if markerID is not None:
                self._invokeMarker(markerID, 'notifyVehicleInCircle', True)
            return

    def __onVehicleLeft(self, type_, idx):
        if type_ != PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE:
            return
        else:
            markerID = None
            if idx in self._markers:
                markerID = self._markers[idx].getMarkerID()
            if markerID is not None:
                self.__insideCircle = INVALID_TARGET_ID
                self._invokeMarker(markerID, 'notifyVehicleInCircle', False)
            return

    def __onSectorBaseAdded(self, sectorBase, isInBase=False):
        markerID = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.SECTOR_BASE_TYPE, sectorBase.position + settings.MARKER_POSITION_ADJUSTMENT)
        if markerID is None:
            return
        else:
            self._setMarkerSticky(markerID, isInBase)
            self._setMarkerActive(markerID, sectorBase.active())
            self._setMarkerRenderInfo(markerID, _MEDIUM_MARKER_MIN_SCALE, _SECTOR_BASES_BOUNDS, _INNER_SECTOR_BASES_BOUNDS, _MAX_CULL_DISTANCE, _SECTOR_BASES_BOUNDS_MIN_SCALE)
            if bool(sectorBase.isPlayerTeam()):
                owner = _ALLY_OWNER
            else:
                owner = _ENEMY_OWNER
            self._invokeMarker(markerID, 'setOwningTeam', owner)
            self._invokeMarker(markerID, 'setIdentifier', sectorBase.baseID)
            self._invokeMarker(markerID, 'setIsEpicMarker', True)
            self._invokeMarker(markerID, 'setActive', isInBase)
            marker = self.__clazz(markerID, owner=owner, active=True)
            self._markers[sectorBase.baseID] = marker
            marker.setState(ReplyStateForMarker.NO_ACTION)
            self._setActiveState(marker, marker.getState())
            self.__checkPlayerInsideCircle(sectorBase.baseID)
            return

    def __onSectorBaseCaptured(self, baseId, isPlayerTeam):
        markerID = None
        if baseId in self._markers:
            marker = self._markers[baseId]
            markerID = marker.getMarkerID()
            marker.setOwningTeam(_ALLY_OWNER if isPlayerTeam else 'enemy')
        if markerID is not None:
            if bool(isPlayerTeam):
                owner = _ALLY_OWNER
            else:
                owner = 'enemy'
            self._invokeMarker(markerID, 'setOwningTeam', owner)
            self.__capturedBases.append(baseId)
        if baseId == self.__highlightedBaseID:
            self._invokeMarker(markerID, 'setActive', False)
            self._setMarkerSticky(markerID, False)
            self.__highlightedBaseID = INVALID_TARGET_ID
        return

    def __getMarkerIDForBaseID(self, baseId):
        markerID = None
        if baseId in self._markers:
            markerID = self._markers[baseId].getMarkerID()
        return markerID

    def __onSectorBasePointsUpdate(self, baseId, isPlayerTeam, points, capturingStopped, invadersCount, expectedCaptureTime):
        markerID = self.__getMarkerIDForBaseID(baseId)
        if markerID is not None:
            self._invokeMarker(markerID, 'setCapturePoints', points)
        return

    def __onSectorBaseActiveStateChanged(self, baseId, isActive):
        markerID = self.__getMarkerIDForBaseID(baseId)
        if markerID is not None:
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
                if self._isInFreeSpectatorMode:
                    self._setMarkerActive(markerID, isActive)
            else:
                self.__checkPlayerInsideCircle(baseId)
                self._setMarkerActive(markerID, isActive)
        return

    def __checkPlayerInsideCircle(self, baseId):
        markerID = self.__getMarkerIDForBaseID(baseId)
        if markerID is not None:
            self._invokeMarker(markerID, 'notifyVehicleInCircle', self.__insideCircle == baseId)
        return


class HeadquartersPlugin(EpicMissionsPlugin, ChatCommunicationComponent):
    __slots__ = ('_markers', '__isHQBattle', '__visibleHQ', '_isInFreeSpectatorMode', '__hqMissionActive', '__clazz')

    def __init__(self, parentObj, clazz=BaseMarker):
        super(HeadquartersPlugin, self).__init__(parentObj)
        self._markers = {}
        self.__isHQBattle = False
        self.__visibleHQ = INVALID_TARGET_ID
        self._isInFreeSpectatorMode = False
        self.__hqMissionActive = False
        self.__clazz = clazz
        ChatCommunicationComponent.__init__(self, parentObj)

    def start(self):
        super(HeadquartersPlugin, self).start()
        ChatCommunicationComponent.start(self)
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded += self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityRemoved += self.__onDestructibleEntityRemoved
            destructibleComponent.onDestructibleEntityStateChanged += self.__onDestructibleEntityStateChanged
            destructibleComponent.onDestructibleEntityHealthChanged += self.__onDestructibleEntityHealthChanged
            hqs = destructibleComponent.destructibleEntities
            for hq in hqs.itervalues():
                self.__onDestructibleEntityAdded(hq)

        else:
            LOG_ERROR('Expected DestructibleEntityComponent not present!')
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived += self.__onMinimapFeedbackReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
            ctrl.setInFocusForPlayer += self.__setInFocusForPlayer
            ctrl.onVehicleFeedbackReceived += self._onVehicleFeedbackReceived
        return

    def stop(self):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded -= self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityRemoved -= self.__onDestructibleEntityRemoved
            destructibleComponent.onDestructibleEntityStateChanged -= self.__onDestructibleEntityStateChanged
            destructibleComponent.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityHealthChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapFeedbackReceived -= self.__onMinimapFeedbackReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
            ctrl.setInFocusForPlayer -= self.__setInFocusForPlayer
            ctrl.onVehicleFeedbackReceived -= self._onVehicleFeedbackReceived
        for marker in self._markers:
            self._destroyMarker(marker.getMarkerID())

        self._markers.clear()
        super(HeadquartersPlugin, self).stop()
        ChatCommunicationComponent.stop(self)
        return

    def resetHQHighlight(self):
        marker = self._markers.get(self.__visibleHQ, None)
        if marker is None:
            return
        else:
            markerID = marker.getMarkerID()
            if not marker.getIsRepliedByPlayer():
                self._setMarkerSticky(markerID, False)
            self._invokeMarker(markerID, 'setHighlight', False)
            self.__visibleHQ = INVALID_TARGET_ID
            return

    def getMarkerType(self):
        return MarkerType.HEADQUARTER_MARKER_TYPE

    def getTargetIDFromMarkerID(self, markerID):
        for targetID, marker in self._markers.iteritems():
            if marker.getMarkerID() == markerID:
                return targetID

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        if targetID == INVALID_MARKER_ID or targetID not in self._markers:
            return INVALID_MARKER_SUBTYPE
        isAttacker = avatar_getter.getPlayerTeam() == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER
        return DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE if isAttacker else DefaultMarkerSubType.ALLY_MARKER_SUBTYPE

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
            marker = self._markers.get(objID, None)
            if marker is None:
                return
            markerID = marker.getMarkerID()
            if markerID and not self._isInFreeSpectatorMode:
                if not EpicMissionsPlugin._getAnyMarkerRepliedByPlayer(self._markers):
                    self._setMarkerSticky(markerID, True)
                self._invokeMarker(markerID, 'setHighlight', True)
        return

    def _updateHighlight(self):
        marker = self._markers.get(self.__visibleHQ, None)
        if marker is None:
            return
        else:
            markerID = marker.getMarkerID()
            self._setMarkerSticky(markerID, not self._isInFreeSpectatorMode)
            self._invokeMarker(markerID, 'setHighlight', not self._isInFreeSpectatorMode)
            return

    def _getMarkerFromTargetID(self, targetID, markerType):
        return None if targetID not in self._markers or markerType != self.getMarkerType() else self._markers[targetID]

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == _EVENT_ID.ENTITY_IN_FOCUS:
            self.__onHQInFocus(vehicleID, value)

    def __onHQInFocus(self, hqEntityID, entityInFocusData):
        if entityInFocusData.entityTypeInFocus != ENTITY_IN_FOCUS_TYPE.DESTRUCTIBLE_ENTITY:
            return
        else:
            markerID = INVALID_MARKER_ID
            if hqEntityID <= 0:
                self._setMarkerObjectInFocus(markerID, entityInFocusData.isInFocus)
                return
            destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is None:
                _logger.error('Expected DestructibleEntityComponent not present!')
                self._setMarkerObjectInFocus(markerID, entityInFocusData.isInFocus)
                return
            hq, targetID = destructibleComponent.getDestructibleEntityAndDestructibleIDByEntityID(hqEntityID)
            if hq is None:
                _logger.error('Expected DestructibleEntity not present! Id: ' + str(hqEntityID))
                self._setMarkerObjectInFocus(markerID, entityInFocusData.isInFocus)
                return
            focusedMarker = self._markers.get(targetID, None)
            if hq.isAlive() and focusedMarker is not None and avatar_getter.isVehicleAlive():
                markerID = focusedMarker.getMarkerID()
            self._setMarkerObjectInFocus(markerID, entityInFocusData.isInFocus)
            return

    def __setInFocusForPlayer(self, oldTargetID, oldTargetType, newTargetID, newTargetType, oneShot):
        if oldTargetType == self.getMarkerType() and oldTargetID in self._markers:
            self.__makeMarkerSticky(oldTargetID, False)
        if newTargetType == self.getMarkerType() and newTargetID in self._markers:
            self.__makeMarkerSticky(newTargetID, True)
        if oneShot:
            return
        if newTargetID == INVALID_TARGET_ID and self.__visibleHQ != INVALID_TARGET_ID:
            self.__makeMarkerSticky(self.__visibleHQ, True)
        elif newTargetID != INVALID_TARGET_ID and self.__visibleHQ != INVALID_TARGET_ID and newTargetID != self.__visibleHQ:
            self.__makeMarkerSticky(self.__visibleHQ, False)

    def __makeMarkerSticky(self, targetID, setSticky):
        marker = self._markers[targetID]
        markerID = marker.getMarkerID()
        self._setMarkerSticky(markerID, setSticky)
        marker.setIsSticky(setSticky)
        self._checkNextState(marker)

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
                _logger.error('Expected DestructibleEntityComponent not present!')
            return

    def __onDestructibleEntityAdded(self, entity):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is None:
            _logger.error('Expected DestructibleEntityComponent not present!')
            return
        elif entity is None:
            _logger.error('Expected DestructibleEntity not present!')
            return
        else:
            handle = self._createMarkerWithMatrix(settings.MARKER_SYMBOL_NAME.HEADQUARTER_TYPE, self.__getMarkerMatrix(entity))
            if handle is None:
                return
            isDead = False
            if entity.health <= 0:
                isDead = True
            self._setMarkerActive(handle, entity.isActive)
            self._setMarkerRenderInfo(handle, _MEDIUM_MARKER_MIN_SCALE, _HEADQUARTERS_BOUNDS, _INNER_HEADQUARTERS_BOUNDS, _MAX_CULL_DISTANCE, _HEADQUARTERS_BOUNDS_MIN_SCALE)
            self._invokeMarker(handle, 'setOwningTeam', entity.isPlayerTeam)
            self._invokeMarker(handle, 'setDead', isDead)
            self._invokeMarker(handle, 'setIdentifier', entity.destructibleEntityID)
            self._invokeMarker(handle, 'setMaxHealth', entity.maxHealth)
            self._invokeMarker(handle, 'setHealth', int(entity.health))
            if bool(entity.isPlayerTeam):
                owner = _ALLY_OWNER
            else:
                owner = 'enemy'
            marker = self.__clazz(handle, True, owner)
            self._markers[entity.destructibleEntityID] = marker
            if entity.destructibleEntityID == self.__visibleHQ:
                self._onNearestObjectiveChanged(entity.destructibleEntityID, None)
            else:
                self._setMarkerSticky(handle, False)
                self._invokeMarker(handle, 'setHighlight', False)
            marker.setState(ReplyStateForMarker.NO_ACTION)
            self._setActiveState(marker, marker.getState())
            if isDead:
                self._setMarkerBoundEnabled(handle, False)
            return

    def __onDestructibleEntityRemoved(self, entityId):
        marker = self._markers.pop(entityId, None)
        if marker is not None:
            self._destroyMarker(marker.getMarkerID())
            if self.__visibleHQ == entityId:
                self.__visibleHQ = INVALID_TARGET_ID
        return

    def __onDestructibleEntityStateChanged(self, entityId):
        marker = self._markers.get(entityId, None)
        if marker is not None:
            destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is None:
                _logger.error('Expected DestructibleEntityComponent not present!')
                return
            hq = destructibleComponent.getDestructibleEntity(entityId)
            if hq is None:
                _logger.error('Expected DestructibleEntity not present! Id: ' + str(entityId))
                return
            markerID = marker.getMarkerID()
            self._setMarkerMatrix(markerID, self.__getMarkerMatrix(hq))
            if not hq.isAlive():
                self._invokeMarker(markerID, 'setHealth', 0)
                self._invokeMarker(markerID, 'setDead', True)
                self._setMarkerSticky(markerID, False)
                self._setMarkerBoundEnabled(markerID, False)
                self.__onRemoveCommandReceived(entityId, self.getMarkerType())
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
        marker = self._markers.get(entityId, None)
        if marker is None:
            return
        else:
            aInfo = self.sessionProvider.getArenaDP().getVehicleInfo(attackerID)
            vehDmg = self.__getVehicleDamageType(aInfo)
            self._invokeMarker(marker.getMarkerID(), 'setHealth', newHealth, vehDmg, hitFlags & VEHICLE_HIT_FLAGS.IS_ANY_PIERCING_MASK)
            return

    def __activateDestructibleMarker(self, entityId, isActive):
        marker = self._markers.get(entityId, None)
        if marker is not None:
            self._setMarkerActive(marker.getMarkerID(), isActive)
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
        if eventID == _EVENT_ID.MINIMAP_MARK_OBJECTIVE:
            self.__doAttentionToHQ(entityID, *value)

    def __doAttentionToHQ(self, senderID, hqId, duration, cmdName):
        marker = self._markers.get(hqId, None)
        if marker is None:
            return
        else:
            marker.setState(ReplyStateForMarker.CREATE_STATE)
            marker.setActiveCommandID(hqId)
            if cmdName in AUTOCOMMIT_COMMAND_NAMES:
                marker.setIsSticky(senderID == avatar_getter.getPlayerVehicleID())
                self._setMarkerRepliesAndCheckState(marker, 1, senderID == avatar_getter.getPlayerVehicleID())
            else:
                self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
            self._checkNextState(marker)
            if not avatar_getter.isVehicleAlive() and marker.getBoundCheckEnabled():
                marker.setBoundCheckEnabled(False)
                self._setMarkerBoundEnabled(marker.getMarkerID(), False)
            return

    def __onRemoveCommandReceived(self, removeID, markerType):
        if markerType != MarkerType.HEADQUARTER_MARKER_TYPE or removeID not in self._markers:
            return
        marker = self._markers[removeID]
        marker.setActiveCommandID(INVALID_COMMAND_ID)
        if marker.getReplyCount() != 0:
            marker.setIsRepliedByPlayer(False)
            self._setMarkerReplied(marker, False)
            self._setMarkerReplyCount(marker, 0)
        self._checkNextState(marker)


class StepRepairPointPlugin(plugins.MarkerPlugin):
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
            _logger.error('Expected StepRepairPointComponent not present!')
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
            _logger.error('Expected StepRepairPointComponent not present!')
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
            self._setMarkerRenderInfo(handle, _SMALL_MARKER_MIN_SCALE, _EMPTY_MARKER_BOUNDS, _EMPTY_MARKER_INNER_BOUNDS, _NEAR_MARKER_CULL_DISTANCE, _SECTOR_BASES_BOUNDS_MIN_SCALE)
            self.__markers[stepRepairPoint.id] = handle
            return

    def __onStepRepairPointActiveStateChanged(self, pointId, isActive):
        handle = self.__markers[pointId]
        if handle is not None:
            self._setMarkerActive(handle, isActive)
        return


class SectorWarningPlugin(plugins.MarkerPlugin):
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
            _logger.error('Expected SectorWarningComponent not present!')
        return

    def start(self):
        super(SectorWarningPlugin, self).start()
        sectorWarningComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorWarningComponent', None)
        if sectorWarningComponent is not None:
            if sectorWarningComponent.warnings is not None:
                for edgeID, warning in sectorWarningComponent.warnings.iteritems():
                    self.__onShowSectorWarning(edgeID, warning.type, warning.targetSectorGroup)

        else:
            _logger.error('Expected SectorWarningComponent not present!')
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
            _logger.error('Expected SectorComponent not present!')
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
            _logger.error('Expected SectorWarningComponent not present!')
            return
        elif None in (edgeID, warningID, targetSectorGroupID):
            _logger.error('[SectorWarningPlugin] Wrong argument!')
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
                self._setMarkerRenderInfo(marker.markerID, _SMALL_MARKER_MIN_SCALE, _EMPTY_MARKER_BOUNDS, _EMPTY_MARKER_INNER_BOUNDS, _NEAR_MARKER_CULL_DISTANCE, _SECTOR_BASES_BOUNDS_MIN_SCALE)
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


class SectorWaypointsPlugin(plugins.MarkerPlugin, IVehiclesAndPositionsController):
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
            _logger.error('Expected SectorBaseComponent not present!')
        component = getattr(componentSystem, 'sectorComponent', None)
        if component is not None:
            component.onWaypointsForPlayerActivated += self.__onWaypointsForPlayerActivated
        else:
            _logger.error('Expected SectorComponent not present!')
        component = getattr(componentSystem, 'sectorWarningComponent', None)
        if component is not None:
            componentSystem.sectorWarningComponent.onTransitionTimerUpdated += self.__onTransitionTimerUpdated
        else:
            _logger.error('Expected SectorWarningComponent not present!')
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
            _logger.error('Expected SectorComponent not present!')
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
                _logger.error('Expected SectorComponent not present!')
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
                        _logger.error('Expected PlayerDataComponent not present!')
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
            _logger.error('Expected SectorComponent not present!')
            return
        else:
            playerData = getattr(componentSystem, 'playerDataComponent', None)
            if playerData is None:
                _logger.error('Expected PlayerDataComponent not present!')
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
            self._setMarkerRenderInfo(self.__marker, _MEDIUM_MARKER_MIN_SCALE, _EMPTY_MARKER_BOUNDS, _EMPTY_MARKER_INNER_BOUNDS, _MAX_CULL_DISTANCE, _SECTOR_BASES_BOUNDS_MIN_SCALE)
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
            _logger.error('Expected SectorBaseComponent not present!')
            return
        else:
            playerData = getattr(componentSystem, 'playerDataComponent', None)
            if playerData is None:
                _logger.error('Expected PlayerDataComponent not present!')
                return
            baseLane = sectorBaseComp.getSectorForSectorBase(baseId).playerGroup
            if baseLane == playerData.physicalLane:
                self.__suspendedForBase = baseId
                self.__suspendedForLane = baseLane
            return


class EpicMarkersManager(MarkersManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

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
