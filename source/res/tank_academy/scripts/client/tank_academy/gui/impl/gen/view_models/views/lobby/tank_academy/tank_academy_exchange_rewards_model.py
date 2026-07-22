# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_exchange_rewards_model.py
from frameworks.wulf import ViewModel

class TankAcademyExchangeRewardsModel(ViewModel):
    __slots__ = ('onConfirm', 'onClose')

    def __init__(self, properties=3, commands=2):
        super(TankAcademyExchangeRewardsModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleUserName(self):
        return self._getString(1)

    def setVehicleUserName(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(TankAcademyExchangeRewardsModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleUserName', '')
        self._addNumberProperty('level', 0)
        self.onConfirm = self._addCommand('onConfirm')
        self.onClose = self._addCommand('onClose')
