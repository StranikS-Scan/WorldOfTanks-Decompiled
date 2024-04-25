# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_slot_model.py
from enum import Enum
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel

class FrontmanRole(Enum):
    ENGINEER = 'engineer'
    AVIATION = 'aviation'
    ARTILLERY = 'artillery'
    NONE = ''


class HbSlotModel(SlotModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(HbSlotModel, self).__init__(properties=properties, commands=commands)

    def getBannedMessage(self):
        return self._getBool(12)

    def setBannedMessage(self, value):
        self._setBool(12, value)

    def getIsProfiledVehicle(self):
        return self._getBool(13)

    def setIsProfiledVehicle(self, value):
        self._setBool(13, value)

    def getSpeciality(self):
        return FrontmanRole(self._getString(14))

    def setSpeciality(self, value):
        self._setString(14, value.value)

    def getSpecialityTooltipHead(self):
        return self._getString(15)

    def setSpecialityTooltipHead(self, value):
        self._setString(15, value)

    def getSpecialityTooltipBody(self):
        return self._getString(16)

    def setSpecialityTooltipBody(self, value):
        self._setString(16, value)

    def getVehicleImage(self):
        return self._getResource(17)

    def setVehicleImage(self, value):
        self._setResource(17, value)

    def _initialize(self):
        super(HbSlotModel, self)._initialize()
        self._addBoolProperty('bannedMessage', False)
        self._addBoolProperty('isProfiledVehicle', False)
        self._addStringProperty('speciality')
        self._addStringProperty('specialityTooltipHead', '')
        self._addStringProperty('specialityTooltipBody', '')
        self._addResourceProperty('vehicleImage', R.invalid())
