# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/deconstruction_device_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.tank_setup.deconstruct_item_model import DeconstructItemModel

class DeconstructionDeviceViewModel(ViewModel):
    __slots__ = ('onOkClick', 'onCloseClick', 'onModuleAdd', 'onModuleReduce')

    def __init__(self, properties=7, commands=4):
        super(DeconstructionDeviceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentVehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentVehicleInfoType():
        return VehicleInfoModel

    def getEquipCoinsOnAccount(self):
        return self._getNumber(1)

    def setEquipCoinsOnAccount(self, value):
        self._setNumber(1, value)

    def getEquipCoinsForDeconstruction(self):
        return self._getNumber(2)

    def setEquipCoinsForDeconstruction(self, value):
        self._setNumber(2, value)

    def getEquipCoinsNeededForUpgrade(self):
        return self._getNumber(3)

    def setEquipCoinsNeededForUpgrade(self, value):
        self._setNumber(3, value)

    def getDeviceForUpgradeName(self):
        return self._getString(4)

    def setDeviceForUpgradeName(self, value):
        self._setString(4, value)

    def getModulesInStorage(self):
        return self._getArray(5)

    def setModulesInStorage(self, value):
        self._setArray(5, value)

    @staticmethod
    def getModulesInStorageType():
        return DeconstructItemModel

    def getModulesOnVehicles(self):
        return self._getArray(6)

    def setModulesOnVehicles(self, value):
        self._setArray(6, value)

    @staticmethod
    def getModulesOnVehiclesType():
        return DeconstructItemModel

    def _initialize(self):
        super(DeconstructionDeviceViewModel, self)._initialize()
        self._addViewModelProperty('currentVehicleInfo', VehicleInfoModel())
        self._addNumberProperty('equipCoinsOnAccount', 0)
        self._addNumberProperty('equipCoinsForDeconstruction', 0)
        self._addNumberProperty('equipCoinsNeededForUpgrade', 0)
        self._addStringProperty('deviceForUpgradeName', '')
        self._addArrayProperty('modulesInStorage', Array())
        self._addArrayProperty('modulesOnVehicles', Array())
        self.onOkClick = self._addCommand('onOkClick')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onModuleAdd = self._addCommand('onModuleAdd')
        self.onModuleReduce = self._addCommand('onModuleReduce')
