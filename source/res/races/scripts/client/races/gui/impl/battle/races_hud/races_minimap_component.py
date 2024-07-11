# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/battle/races_hud/races_minimap_component.py
import math
import BigWorld
from races.gui.impl.gen.view_models.views.battle.races_hud.races_minimap_positions import RacesMinimapPositions
_UPDATE_POSITIONS_SEC = 0.1

class PositionsRepository(object):
    MIN_SQUARE_DISTANCE = 25
    MIN_ANGLE = 1

    def __init__(self):
        self.__vehicles = {}

    def checkDeviation(self, vehicleID, positions, angle):
        if vehicleID not in self.__vehicles:
            self.__vehicles.update({vehicleID: {'positions': positions,
                         'angle': angle}})
        else:
            oldPositions = self.__vehicles[vehicleID]['positions']
            squareDistance = sum([ (a - b) ** 2 for a, b in zip(oldPositions, positions) ])
            angleDeviation = abs(self.__vehicles[vehicleID]['angle'] - angle)
            if squareDistance > self.MIN_SQUARE_DISTANCE or angleDeviation > self.MIN_ANGLE:
                self.__vehicles.update({vehicleID: {'positions': positions,
                             'angle': angle}})
                return True
        return False

    @property
    def vehicles(self):
        return self.__vehicles


class RacesMinimapComponent(object):

    def __init__(self, viewModel, sessionProvider):
        self.viewModel = viewModel
        self.sessionProvider = sessionProvider
        self.positionsRepository = PositionsRepository()

    def positionAngleVehicleIDGenerator(self, ownVehicle):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            vID = vInfo.vehicleID
            vehicle = BigWorld.entity(vID)
            if vID != ownVehicle.id:
                if vehicle:
                    positions, angle = self.__getVehiclePositions(vehicle)
                else:
                    positions = self.sessionProvider.arenaVisitor.getArenaPositions().get(vID)
                    if not positions:
                        continue
                    angle = self.positionsRepository.vehicles.get(vID)['angle']
                yield (positions, angle, vID)

    def onPositionsUpdate(self):
        vehiclePositionsForUpdate = dict()
        ownVehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        for positions, angle, vID in self.positionAngleVehicleIDGenerator(ownVehicle):
            if self.positionsRepository.checkDeviation(vID, positions, angle):
                vehiclePositionsForUpdate.update({vID: [positions, angle]})

        if vehiclePositionsForUpdate:
            self.__updatePositions(vehiclePositionsForUpdate)
        vehiclePositionsForUpdate.clear()
        if ownVehicle:
            ownVehiclePosition, ownAngle = self.__getVehiclePositions(ownVehicle)
            if self.positionsRepository.checkDeviation(ownVehicle.id, ownVehiclePosition, ownAngle):
                self.__updateOwnVehiclePosition(ownVehiclePosition, ownAngle)
        return _UPDATE_POSITIONS_SEC

    def __updateOwnVehiclePosition(self, ownVehiclePosition, ownAngle):
        with self.viewModel.transaction() as tx:
            tx.minimapComponent.setOwnVehiclePosX(ownVehiclePosition[0])
            tx.minimapComponent.setOwnVehiclePosY(ownVehiclePosition[2])
            tx.minimapComponent.setOwnVehicleAngle(ownAngle)

    def __getVehiclePositions(self, vehicle):
        positions = vehicle.position
        angle = math.degrees(vehicle.yaw)
        return (positions, angle)

    def __updatePositions(self, vehiclePositionsForUpdate):
        with self.viewModel.transaction() as tx:
            modelVehicles = tx.minimapComponent.getVehicles()
            if modelVehicles:
                for vehicle in modelVehicles:
                    positions = vehiclePositionsForUpdate.get(vehicle.getVehicleID())
                    if positions:
                        vehicle.setPosX(positions[0][0])
                        vehicle.setPosY(positions[0][2])
                        vehicle.setAngle(positions[1])

            modelVehicles.invalidate()

    def setMinimapVehiclePositions(self):
        bottomLeft, topRight = self.sessionProvider.arenaVisitor.type.getBoundingBox()
        ownVehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
        with self.viewModel.transaction() as tx:
            modelVehicles = tx.minimapComponent.getVehicles()
            for positions, angle, vID in self.positionAngleVehicleIDGenerator(ownVehicle):
                positionsModel = RacesMinimapPositions()
                positionsModel.setVehicleID(vID)
                positionsModel.setPosX(positions[0])
                positionsModel.setPosY(positions[2])
                positionsModel.setAngle(angle)
                modelVehicles.addViewModel(positionsModel)

            ownVehiclePosition, ownAngle = self.__getVehiclePositions(ownVehicle)
            self.__updateOwnVehiclePosition(ownVehiclePosition, ownAngle)
            tx.minimapComponent.setArenaBottomLeftX(bottomLeft[0])
            tx.minimapComponent.setArenaBottomLeftY(bottomLeft[1])
            tx.minimapComponent.setArenaTopRightX(topRight[0])
            tx.minimapComponent.setArenaTopRightY(topRight[1])
            tx.minimapComponent.setMinimapName(self.sessionProvider.arenaVisitor.type.getGeometryName())
