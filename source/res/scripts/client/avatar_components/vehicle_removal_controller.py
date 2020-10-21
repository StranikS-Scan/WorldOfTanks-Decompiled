# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/vehicle_removal_controller.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import uniprof

class VehicleRemovalController(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__effectPlayers = []

    def onBecomePlayer(self):
        pass

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomeNonPlayer(self):
        for effectPlayer in self.__effectPlayers:
            effectPlayer.stopEffect()

    @uniprof.regionDecorator(label='VehicleRemovalController.removeVehicle', scope='wrap')
    def removeVehicle(self, vehID, effect):
        vehicle = BigWorld.entity(vehID)
        if vehicle is None:
            return
        else:
            vehicle.show(False)
            return
