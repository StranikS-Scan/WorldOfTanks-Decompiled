# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/battle/ban_entry_point_model.py
from comp7.gui.impl.gen.view_models.views.battle.enums import BanState
from frameworks.wulf import ViewModel
from comp7.gui.impl.gen.view_models.views.battle.comp7_vehicle_model import Comp7VehicleModel

class BanEntryPointModel(ViewModel):
    __slots__ = ('onOpen', 'pollServerTime')

    def __init__(self, properties=7, commands=2):
        super(BanEntryPointModel, self).__init__(properties=properties, commands=commands)

    @property
    def bannedByAlliesVehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getBannedByAlliesVehicleType():
        return Comp7VehicleModel

    @property
    def bannedByEnemiesVehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getBannedByEnemiesVehicleType():
        return Comp7VehicleModel

    def getState(self):
        return BanState(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getEndTimestamp(self):
        return self._getNumber(3)

    def setEndTimestamp(self, value):
        self._setNumber(3, value)

    def getServerTimestamp(self):
        return self._getNumber(4)

    def setServerTimestamp(self, value):
        self._setNumber(4, value)

    def getAlliesVehicleCD(self):
        return self._getNumber(5)

    def setAlliesVehicleCD(self, value):
        self._setNumber(5, value)

    def getEnemiesVehicleCD(self):
        return self._getNumber(6)

    def setEnemiesVehicleCD(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(BanEntryPointModel, self)._initialize()
        self._addViewModelProperty('bannedByAlliesVehicle', Comp7VehicleModel())
        self._addViewModelProperty('bannedByEnemiesVehicle', Comp7VehicleModel())
        self._addStringProperty('state')
        self._addNumberProperty('endTimestamp', 0)
        self._addNumberProperty('serverTimestamp', 0)
        self._addNumberProperty('alliesVehicleCD', -1)
        self._addNumberProperty('enemiesVehicleCD', -1)
        self.onOpen = self._addCommand('onOpen')
        self.pollServerTime = self._addCommand('pollServerTime')
