# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/nation_item_info_view_model.py
from frameworks.wulf import ViewModel

class NationItemInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NationItemInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getAmount(self):
        return self._getNumber(1)

    def setAmount(self, value):
        self._setNumber(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NationItemInfoViewModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('amount', 0)
        self._addBoolProperty('isSelected', False)
