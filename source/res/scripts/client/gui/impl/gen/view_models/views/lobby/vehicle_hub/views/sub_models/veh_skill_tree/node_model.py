# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/veh_skill_tree/node_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel

class Status(Enum):
    RESEARCHED = 'researched'
    SELECTED = 'selected'
    DEFAULT = 'default'


class Type(Enum):
    MAJOR = 'major'
    SPECIAL = 'special'
    FINAL = 'final'
    COMMON = 'common'
    GHOST = 'ghost'


class NodeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(NodeModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getX(self):
        return self._getNumber(1)

    def setX(self, value):
        self._setNumber(1, value)

    def getY(self):
        return self._getNumber(2)

    def setY(self, value):
        self._setNumber(2, value)

    def getStatus(self):
        return Status(self._getString(3))

    def setStatus(self, value):
        self._setString(3, value.value)

    def getIsHintRequired(self):
        return self._getBool(4)

    def setIsHintRequired(self, value):
        self._setBool(4, value)

    def getType(self):
        return Type(self._getString(5))

    def setType(self, value):
        self._setString(5, value.value)

    def getPrice(self):
        return self._getReal(6)

    def setPrice(self, value):
        self._setReal(6, value)

    def getIconName(self):
        return self._getString(7)

    def setIconName(self, value):
        self._setString(7, value)

    def getLocalizationName(self):
        return self._getString(8)

    def setLocalizationName(self, value):
        self._setString(8, value)

    def getVehicleName(self):
        return self._getString(9)

    def setVehicleName(self, value):
        self._setString(9, value)

    def getCategories(self):
        return self._getArray(10)

    def setCategories(self, value):
        self._setArray(10, value)

    @staticmethod
    def getCategoriesType():
        return unicode

    def _initialize(self):
        super(NodeModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('x', 0)
        self._addNumberProperty('y', 0)
        self._addStringProperty('status')
        self._addBoolProperty('isHintRequired', False)
        self._addStringProperty('type')
        self._addRealProperty('price', 0.0)
        self._addStringProperty('iconName', '')
        self._addStringProperty('localizationName', '')
        self._addStringProperty('vehicleName', '')
        self._addArrayProperty('categories', Array())
