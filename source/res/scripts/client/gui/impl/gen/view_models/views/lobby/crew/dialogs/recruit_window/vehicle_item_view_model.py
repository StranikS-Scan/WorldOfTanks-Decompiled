# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/recruit_window/vehicle_item_view_model.py
from frameworks.wulf import ViewModel

class VehicleItemViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(VehicleItemViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIsElite(self):
        return self._getBool(1)

    def setIsElite(self, value):
        self._setBool(1, value)

    def getIsIGR(self):
        return self._getBool(2)

    def setIsIGR(self, value):
        self._setBool(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def getName(self):
        return self._getString(4)

    def setName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(VehicleItemViewModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isIGR', False)
        self._addStringProperty('type', '')
        self._addStringProperty('name', '')
