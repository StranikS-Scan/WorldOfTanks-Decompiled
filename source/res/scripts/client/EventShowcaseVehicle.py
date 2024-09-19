# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventShowcaseVehicle.py
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from EventVehicle import _EventVehicleAppearance
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IEventBattlesController

class EventShowcaseVehicle(ClientSelectableCameraVehicle):
    __gameEventController = dependency.descriptor(IEventBattlesController)

    def onEnterWorld(self, prereqs):
        super(EventShowcaseVehicle, self).onEnterWorld(prereqs)
        eventShowcaseVehName = self.__gameEventController.getEventShowcaseVehicle()
        vDescriptor = vehicles.VehicleDescr(typeName=eventShowcaseVehName)
        self.recreateVehicle(vDescriptor)

    def setHighlight(self, show, fallback=False):
        pass

    def onMouseClick(self):
        pass

    def onDeselect(self):
        pass

    def _createAppearance(self):
        return _EventVehicleAppearance(self.spaceID, self)
