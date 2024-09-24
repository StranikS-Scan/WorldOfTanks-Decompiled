# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/subcategory_info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.subcategory_info_value_view_model import SubcategoryInfoValueViewModel

class SubcategoryInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SubcategoryInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getList(self):
        return self._getArray(1)

    def setList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getListType():
        return SubcategoryInfoValueViewModel

    def _initialize(self):
        super(SubcategoryInfoViewModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addArrayProperty('list', Array())
