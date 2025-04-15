# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/sort_dropdown_item_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class SortingTypeEnum(IntEnum):
    DEFAULT = 0
    COMMON = 1
    LEGENDARY = 2


class SortDropdownItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SortDropdownItemModel, self).__init__(properties=properties, commands=commands)

    def getIsSelected(self):
        return self._getBool(0)

    def setIsSelected(self, value):
        self._setBool(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getMType(self):
        return SortingTypeEnum(self._getNumber(2))

    def setMType(self, value):
        self._setNumber(2, value.value)

    def _initialize(self):
        super(SortDropdownItemModel, self)._initialize()
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isEnabled', False)
        self._addNumberProperty('mType', SortingTypeEnum.DEFAULT.value)
