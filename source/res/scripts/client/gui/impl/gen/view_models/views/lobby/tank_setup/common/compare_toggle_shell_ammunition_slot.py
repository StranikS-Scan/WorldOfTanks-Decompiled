# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/compare_toggle_shell_ammunition_slot.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.vehicle_mechanic_model import VehicleMechanicModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.compare_toggle_ammunition_slot import CompareToggleAmmunitionSlot

class CompareToggleShellAmmunitionSlot(CompareToggleAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(CompareToggleShellAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    def getMechanics(self):
        return self._getArray(15)

    def setMechanics(self, value):
        self._setArray(15, value)

    @staticmethod
    def getMechanicsType():
        return VehicleMechanicModel

    def _initialize(self):
        super(CompareToggleShellAmmunitionSlot, self)._initialize()
        self._addArrayProperty('mechanics', Array())
