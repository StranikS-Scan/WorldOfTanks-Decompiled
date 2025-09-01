# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/equipments/equipments_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.loadout.base_loadout_model import BaseLoadoutModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_slot_model import OptDeviceSlotModel

class EquipmentsModel(BaseLoadoutModel):
    __slots__ = ('onGetMoreCurrency',)

    def __init__(self, properties=8, commands=2):
        super(EquipmentsModel, self).__init__(properties=properties, commands=commands)

    def getEquipCoinCount(self):
        return self._getNumber(1)

    def setEquipCoinCount(self, value):
        self._setNumber(1, value)

    def getHasChanges(self):
        return self._getBool(2)

    def setHasChanges(self, value):
        self._setBool(2, value)

    def getSimpleEquipments(self):
        return self._getArray(3)

    def setSimpleEquipments(self, value):
        self._setArray(3, value)

    @staticmethod
    def getSimpleEquipmentsType():
        return OptDeviceSlotModel

    def getDeluxEquipments(self):
        return self._getArray(4)

    def setDeluxEquipments(self, value):
        self._setArray(4, value)

    @staticmethod
    def getDeluxEquipmentsType():
        return OptDeviceSlotModel

    def getTrophyEquipments(self):
        return self._getArray(5)

    def setTrophyEquipments(self, value):
        self._setArray(5, value)

    @staticmethod
    def getTrophyEquipmentsType():
        return OptDeviceSlotModel

    def getModernizedEquipments(self):
        return self._getArray(6)

    def setModernizedEquipments(self, value):
        self._setArray(6, value)

    @staticmethod
    def getModernizedEquipmentsType():
        return OptDeviceSlotModel

    def getHasModernizedEquipmentToDisassemble(self):
        return self._getBool(7)

    def setHasModernizedEquipmentToDisassemble(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(EquipmentsModel, self)._initialize()
        self._addNumberProperty('equipCoinCount', 0)
        self._addBoolProperty('hasChanges', False)
        self._addArrayProperty('simpleEquipments', Array())
        self._addArrayProperty('deluxEquipments', Array())
        self._addArrayProperty('trophyEquipments', Array())
        self._addArrayProperty('modernizedEquipments', Array())
        self._addBoolProperty('hasModernizedEquipmentToDisassemble', False)
        self.onGetMoreCurrency = self._addCommand('onGetMoreCurrency')
