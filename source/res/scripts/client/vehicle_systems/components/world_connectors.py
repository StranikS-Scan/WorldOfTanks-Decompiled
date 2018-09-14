# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/world_connectors.py
import BigWorld
from svarog_script import auto_properties
import svarog_script.py_component
from vehicle_systems.tankStructure import TankPartNames

class GunRotatorConnector(svarog_script.py_component.Component):

    def __init__(self, appearance):
        self.__appearance = appearance

    def activate(self):
        soundEffect = BigWorld.player().gunRotator.soundEffect
        if soundEffect is not None:
            soundEffect.connectSoundToMatrix(self.__appearance.compoundModel.node(TankPartNames.TURRET))
        return

    def deactivate(self):
        soundEffect = BigWorld.player().gunRotator.soundEffect
        if soundEffect is not None:
            soundEffect.lockSoundMatrix()
        return

    def destroy(self):
        self.__appearance = None
        self.processVehicleDeath(None)
        return

    def processVehicleDeath(self, vehicleDamageState):
        self.deactivate()
