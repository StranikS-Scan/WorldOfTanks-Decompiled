# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/avatar_input_handler/map_case_mode.py
import BigWorld
from typing import Optional, Any
from BunkerLogicComponent import BunkerLogicComponent
import CGF
from AvatarInputHandler import MapCaseMode
from Math import Vector3
from constants import VEHICLE_BUNKER_TURRET_TAG
POSITION_PRECISION = 0.001

def _vectorEqual(first, second):
    return abs(first.x - second.x) < POSITION_PRECISION and abs(first.y - second.y) < POSITION_PRECISION and abs(first.z - second.z) < POSITION_PRECISION


class StrikeSelector(MapCaseMode._ArcadeBomberStrikeSelector):

    def __init__(self, position, equipment):
        super(StrikeSelector, self).__init__(position, equipment)
        self._edgedBunkers = []

    def destroy(self):
        self._clearEdgedDestructibles()
        super(StrikeSelector, self).destroy()

    def highlightVehicles(self):
        super(StrikeSelector, self).highlightVehicles()
        self._clearEdgedDestructibles()
        for entity in BigWorld.entities.valuesOfType('DestructibleEntity'):
            if self.area.pointInside(entity.position):
                bunkerComponent = self._getBunkerComponent(entity.destructibleEntityID)
                if bunkerComponent:
                    bunkerComponent.highlightBunker(True)
                    self._edgedBunkers.append(bunkerComponent)

    def _validateVehicle(self, vehicle):
        return super(StrikeSelector, self)._validateVehicle(vehicle) and VEHICLE_BUNKER_TURRET_TAG not in vehicle.typeDescriptor.type.tags

    def _clearEdgedDestructibles(self):
        for bunkerComponent in self._edgedBunkers:
            bunkerComponent.highlightBunker(False)

        self._edgedBunkers = []

    @staticmethod
    def _getBunkerComponent(destructibleEntityID):
        bunkerQuery = CGF.Query(BigWorld.player().spaceID, (CGF.GameObject, BunkerLogicComponent))
        return next((bunker for _, bunker in bunkerQuery if bunker.destructibleEntityId == destructibleEntityID), None)


class NavMeshCheckingSelector(MapCaseMode._ArenaBoundsAreaStrikeSelector):
    _CHECK_SERVER_DELAY = 0.1

    def __init__(self, position, equipment, direction=MapCaseMode._DEFAULT_STRIKE_DIRECTION):
        super(NavMeshCheckingSelector, self).__init__(position, equipment, direction)
        self._updateTimerID = None
        self._checkPosition = position
        self._prevCheckPosition = Vector3(0.0, 0.0, 0.0)
        self._avatarComponent.onPositionValidChanged += self._onPositionValidChanged
        self._updateFromServer()
        self._enableWaterCollision(True)
        return

    def processHover(self, position, reset=False):
        self._checkPosition = position
        super(NavMeshCheckingSelector, self).processHover(position, reset)
        self._updateOutFromBoundsPosition(position)

    def processSelection(self, position, reset=False):
        if reset:
            return True
        result = super(NavMeshCheckingSelector, self).processSelection(position, reset)
        if not result:
            self._avatarComponent.onSMAbilityWrongPoint(position)
        return False

    def destroy(self):
        self._avatarComponent.onPositionValidChanged -= self._onPositionValidChanged
        if self._updateTimerID is not None:
            BigWorld.cancelCallback(self._updateTimerID)
            self._updateTimerID = None
        super(NavMeshCheckingSelector, self).destroy()
        return

    @property
    def _avatarComponent(self):
        return BigWorld.player().StoryModeAvatarComponent

    def _validatePosition(self, position):
        return self._avatarComponent.isPositionValid and super(NavMeshCheckingSelector, self)._validatePosition(position)

    def _updateFromServer(self):
        if not _vectorEqual(self._prevCheckPosition, self._checkPosition):
            _, equipmentId = self.equipment.id
            self._avatarComponent.checkPositionForEquipment(equipmentId, self._checkPosition)
            self._prevCheckPosition = Vector3(self._checkPosition)
        self._updateTimerID = BigWorld.callback(self._CHECK_SERVER_DELAY, self._updateFromServer)

    def _onPositionValidChanged(self):
        self._updatePositionsAndVisibility(BigWorld.player().inputHandler.getDesiredShotPoint(True))


class ReconAbilitySelector(NavMeshCheckingSelector):
    pass


class DistractionAbilitySelector(NavMeshCheckingSelector):
    pass
