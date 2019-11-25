# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/nation_change/nation_change_device_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NationChangeDeviceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NationChangeDeviceModel, self).__init__(properties=properties, commands=commands)

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getIsRemovable(self):
        return self._getBool(1)

    def setIsRemovable(self, value):
        self._setBool(1, value)

    def getIsImproved(self):
        return self._getBool(2)

    def setIsImproved(self, value):
        self._setBool(2, value)

    def getIntCD(self):
        return self._getNumber(3)

    def setIntCD(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(NationChangeDeviceModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addBoolProperty('isRemovable', False)
        self._addBoolProperty('isImproved', False)
        self._addNumberProperty('intCD', 0)
