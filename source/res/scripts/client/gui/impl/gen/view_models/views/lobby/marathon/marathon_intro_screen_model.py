# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/marathon_intro_screen_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MarathonIntroScreenModel(ViewModel):
    __slots__ = ('onGoToMarathonClick',)

    def __init__(self, properties=3, commands=1):
        super(MarathonIntroScreenModel, self).__init__(properties=properties, commands=commands)

    def getVehicleLevel(self):
        return self._getNumber(0)

    def setVehicleLevel(self, value):
        self._setNumber(0, value)

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getVehicleIcon(self):
        return self._getResource(2)

    def setVehicleIcon(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(MarathonIntroScreenModel, self)._initialize()
        self._addNumberProperty('vehicleLevel', 0)
        self._addStringProperty('vehicleName', '')
        self._addResourceProperty('vehicleIcon', R.invalid())
        self.onGoToMarathonClick = self._addCommand('onGoToMarathonClick')
