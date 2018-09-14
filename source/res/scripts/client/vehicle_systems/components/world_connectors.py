# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/world_connectors.py
import BigWorld
from vehicle_systems import assembly_utility
from vehicle_systems.tankStructure import TankPartNames

class GunRotatorConnector(assembly_utility.Component):

    def __init__(self, model):
        soundEffect = BigWorld.player().gunRotator.soundEffect
        if soundEffect is not None:
            soundEffect.connectSoundToMatrix(model.node(TankPartNames.TURRET))
        return

    def destroy(self):
        self.processVehicleDeath(None)
        return

    def processVehicleDeath(self, vehicleDamageState):
        soundEffect = BigWorld.player().gunRotator.soundEffect
        if soundEffect is not None:
            soundEffect.lockSoundMatrix()
        return
