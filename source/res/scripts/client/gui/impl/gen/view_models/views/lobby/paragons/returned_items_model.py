# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/returned_items_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.returned_row_model import ReturnedRowModel

class GroupInfoTypes(IntEnum):
    OPTIONALDEVICES = 0
    BATTLEBOOSTERS = 1
    SHELLS = 2
    CUSTOMIZATION = 3
    EQUIPMENTS = 4
    CREW = 5


class ReturnedItemsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ReturnedItemsModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return GroupInfoTypes(self._getNumber(0))

    def setType(self, value):
        self._setNumber(0, value.value)

    def getGroupInfo(self):
        return self._getArray(1)

    def setGroupInfo(self, value):
        self._setArray(1, value)

    @staticmethod
    def getGroupInfoType():
        return ReturnedRowModel

    def _initialize(self):
        super(ReturnedItemsModel, self)._initialize()
        self._addNumberProperty('type')
        self._addArrayProperty('groupInfo', Array())
