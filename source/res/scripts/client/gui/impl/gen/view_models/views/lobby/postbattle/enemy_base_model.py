# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/enemy_base_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class EnemyBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(EnemyBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    def getTankName(self):
        return self._getString(1)

    def setTankName(self, value):
        self._setString(1, value)

    def getShortTankName(self):
        return self._getString(2)

    def setShortTankName(self, value):
        self._setString(2, value)

    def getTankType(self):
        return self._getString(3)

    def setTankType(self, value):
        self._setString(3, value)

    def getVehicleCD(self):
        return self._getNumber(4)

    def setVehicleCD(self, value):
        self._setNumber(4, value)

    def getVehicleID(self):
        return self._getNumber(5)

    def setVehicleID(self, value):
        self._setNumber(5, value)

    def getVehicleIconName(self):
        return self._getString(6)

    def setVehicleIconName(self, value):
        self._setString(6, value)

    def getVehicleLevel(self):
        return self._getNumber(7)

    def setVehicleLevel(self, value):
        self._setNumber(7, value)

    def getDbID(self):
        return self._getNumber(8)

    def setDbID(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(EnemyBaseModel, self)._initialize()
        self._addViewModelProperty('user', UserNameModel())
        self._addStringProperty('tankName', '')
        self._addStringProperty('shortTankName', '')
        self._addStringProperty('tankType', '')
        self._addNumberProperty('vehicleCD', 0)
        self._addNumberProperty('vehicleID', 0)
        self._addStringProperty('vehicleIconName', '')
        self._addNumberProperty('vehicleLevel', 0)
        self._addNumberProperty('dbID', 0)
