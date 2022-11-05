# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/opt_device_ammunition_slot.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specializations_model import SpecializationsModel

class OptDeviceAmmunitionSlot(BaseAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(OptDeviceAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    @property
    def specializations(self):
        return self._getViewModel(11)

    @staticmethod
    def getSpecializationsType():
        return SpecializationsModel

    def getActiveSpecsMask(self):
        return self._getNumber(12)

    def setActiveSpecsMask(self, value):
        self._setNumber(12, value)

    def getIsIncompatible(self):
        return self._getBool(13)

    def setIsIncompatible(self, value):
        self._setBool(13, value)

    def getLevel(self):
        return self._getNumber(14)

    def setLevel(self, value):
        self._setNumber(14, value)

    def _initialize(self):
        super(OptDeviceAmmunitionSlot, self)._initialize()
        self._addViewModelProperty('specializations', SpecializationsModel())
        self._addNumberProperty('activeSpecsMask', 0)
        self._addBoolProperty('isIncompatible', False)
        self._addNumberProperty('level', 0)
