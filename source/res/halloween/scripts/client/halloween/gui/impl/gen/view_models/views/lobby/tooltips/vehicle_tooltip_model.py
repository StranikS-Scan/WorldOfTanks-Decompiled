# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.slot_model import SlotModel

class VehicleTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(VehicleTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleType(self):
        return self._getString(1)

    def setVehicleType(self, value):
        self._setString(1, value)

    def getVehicleState(self):
        return self._getString(2)

    def setVehicleState(self, value):
        self._setString(2, value)

    def getUserName(self):
        return self._getString(3)

    def setUserName(self, value):
        self._setString(3, value)

    def getUserDescription(self):
        return self._getString(4)

    def setUserDescription(self, value):
        self._setString(4, value)

    def getIsElite(self):
        return self._getBool(5)

    def setIsElite(self, value):
        self._setBool(5, value)

    def getIsDailyKeyQuestVisible(self):
        return self._getBool(6)

    def setIsDailyKeyQuestVisible(self, value):
        self._setBool(6, value)

    def getIsStatusVisible(self):
        return self._getBool(7)

    def setIsStatusVisible(self, value):
        self._setBool(7, value)

    def getCrewSlots(self):
        return self._getArray(8)

    def setCrewSlots(self, value):
        self._setArray(8, value)

    @staticmethod
    def getCrewSlotsType():
        return SlotModel

    def _initialize(self):
        super(VehicleTooltipModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleState', '')
        self._addStringProperty('userName', '')
        self._addStringProperty('userDescription', '')
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isDailyKeyQuestVisible', False)
        self._addBoolProperty('isStatusVisible', False)
        self._addArrayProperty('crewSlots', Array())
