# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/tank_setup_action_model.py
from frameworks.wulf import ViewModel

class TankSetupActionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(TankSetupActionModel, self).__init__(properties=properties, commands=commands)

    def getActionType(self):
        return self._getString(0)

    def setActionType(self, value):
        self._setString(0, value)

    def getIntCD(self):
        return self._getNumber(1)

    def setIntCD(self, value):
        self._setNumber(1, value)

    def getInstalledSlotId(self):
        return self._getNumber(2)

    def setInstalledSlotId(self, value):
        self._setNumber(2, value)

    def getLeftID(self):
        return self._getNumber(3)

    def setLeftID(self, value):
        self._setNumber(3, value)

    def getRightID(self):
        return self._getNumber(4)

    def setRightID(self, value):
        self._setNumber(4, value)

    def getLeftIntCD(self):
        return self._getNumber(5)

    def setLeftIntCD(self, value):
        self._setNumber(5, value)

    def getRightIntCD(self):
        return self._getNumber(6)

    def setRightIntCD(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(TankSetupActionModel, self)._initialize()
        self._addStringProperty('actionType', '')
        self._addNumberProperty('intCD', -1)
        self._addNumberProperty('installedSlotId', -1)
        self._addNumberProperty('leftID', -1)
        self._addNumberProperty('rightID', -1)
        self._addNumberProperty('leftIntCD', -1)
        self._addNumberProperty('rightIntCD', -1)
