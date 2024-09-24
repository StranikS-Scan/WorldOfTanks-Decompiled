# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/avatar_input_handler/map_case_mode.py
import BigWorld
from BunkerLogicComponent import BunkerLogicComponent
import CGF
from AvatarInputHandler import MapCaseMode
from constants import VEHICLE_BUNKER_TURRET_TAG

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
