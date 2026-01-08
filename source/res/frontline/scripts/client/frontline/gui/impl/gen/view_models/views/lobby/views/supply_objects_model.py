# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/supply_objects_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class SupplyType(Enum):
    NONE = 'none'
    PILLBOX = 'pillbox'
    MORTAR = 'mortar'
    FLAMER = 'flamer'
    AIRSHIP = 'airship'


class SupplyObjectsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SupplyObjectsModel, self).__init__(properties=properties, commands=commands)

    def getPoint(self):
        return self._getString(0)

    def setPoint(self, value):
        self._setString(0, value)

    def getObject(self):
        return SupplyType(self._getString(1))

    def setObject(self, value):
        self._setString(1, value.value)

    def getObjectId(self):
        return self._getNumber(2)

    def setObjectId(self, value):
        self._setNumber(2, value)

    def getIsHintShow(self):
        return self._getBool(3)

    def setIsHintShow(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SupplyObjectsModel, self)._initialize()
        self._addStringProperty('point', '')
        self._addStringProperty('object')
        self._addNumberProperty('objectId', 0)
        self._addBoolProperty('isHintShow', True)
