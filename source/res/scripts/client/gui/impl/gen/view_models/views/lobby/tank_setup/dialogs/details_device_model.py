# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/details_device_model.py
from frameworks.wulf import ViewModel

class DetailsDeviceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DetailsDeviceModel, self).__init__(properties=properties, commands=commands)

    def getOverlayType(self):
        return self._getString(0)

    def setOverlayType(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getDeviceName(self):
        return self._getString(2)

    def setDeviceName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(DetailsDeviceModel, self)._initialize()
        self._addStringProperty('overlayType', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('deviceName', '')
