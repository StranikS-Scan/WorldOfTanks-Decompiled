# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_slot_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel

class HbSlotModel(SlotModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(HbSlotModel, self).__init__(properties=properties, commands=commands)

    def getBannedMessage(self):
        return self._getBool(12)

    def setBannedMessage(self, value):
        self._setBool(12, value)

    def getIsProfiledVehicle(self):
        return self._getBool(13)

    def setIsProfiledVehicle(self, value):
        self._setBool(13, value)

    def getDivisionID(self):
        return self._getNumber(14)

    def setDivisionID(self, value):
        self._setNumber(14, value)

    def getDivisionLevel(self):
        return self._getNumber(15)

    def setDivisionLevel(self, value):
        self._setNumber(15, value)

    def getVehicleImage(self):
        return self._getResource(16)

    def setVehicleImage(self, value):
        self._setResource(16, value)

    def _initialize(self):
        super(HbSlotModel, self)._initialize()
        self._addBoolProperty('bannedMessage', False)
        self._addBoolProperty('isProfiledVehicle', False)
        self._addNumberProperty('divisionID', 0)
        self._addNumberProperty('divisionLevel', 0)
        self._addResourceProperty('vehicleImage', R.invalid())
