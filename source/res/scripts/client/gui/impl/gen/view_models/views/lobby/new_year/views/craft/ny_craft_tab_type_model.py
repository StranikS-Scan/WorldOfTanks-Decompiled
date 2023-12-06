# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/craft/ny_craft_tab_type_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_tab_type_item_model import NyCraftTabTypeItemModel

class NyCraftTabTypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyCraftTabTypeModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getTypes(self):
        return self._getArray(1)

    def setTypes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getTypesType():
        return NyCraftTabTypeItemModel

    def _initialize(self):
        super(NyCraftTabTypeModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addArrayProperty('types', Array())
