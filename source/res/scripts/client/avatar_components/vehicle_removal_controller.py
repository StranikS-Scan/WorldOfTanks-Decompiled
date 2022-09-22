# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/vehicle_removal_controller.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import uniprof

class VehicleRemovalController(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onBecomePlayer(self):
        pass

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomeNonPlayer(self):
        pass

    @uniprof.regionDecorator(label='VehicleRemovalController.removeVehicle', scope='wrap')
    def removeVehicle(self, vehID):
        self.sessionProvider.shared.feedback.onVehicleMarkerErased(vehID)
        vehicle = BigWorld.entity(vehID)
        if vehicle is None:
            return
        else:
            vehicle.show(False)
            return
