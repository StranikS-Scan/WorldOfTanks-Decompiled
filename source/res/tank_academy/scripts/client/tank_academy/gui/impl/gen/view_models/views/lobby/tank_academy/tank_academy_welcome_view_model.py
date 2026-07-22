# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_welcome_view_model.py
from frameworks.wulf import ViewModel

class TankAcademyWelcomeViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=1, commands=1):
        super(TankAcademyWelcomeViewModel, self).__init__(properties=properties, commands=commands)

    def getVehiclesCount(self):
        return self._getNumber(0)

    def setVehiclesCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(TankAcademyWelcomeViewModel, self)._initialize()
        self._addNumberProperty('vehiclesCount', 0)
        self.onClose = self._addCommand('onClose')
