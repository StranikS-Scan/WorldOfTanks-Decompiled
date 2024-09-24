# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/resource_info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.nation_item_info_view_model import NationItemInfoViewModel

class ResourceInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ResourceInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getBalance(self):
        return self._getNumber(1)

    def setBalance(self, value):
        self._setNumber(1, value)

    def getLimit(self):
        return self._getNumber(2)

    def setLimit(self, value):
        self._setNumber(2, value)

    def getRate(self):
        return self._getNumber(3)

    def setRate(self, value):
        self._setNumber(3, value)

    def getPercent(self):
        return self._getNumber(4)

    def setPercent(self, value):
        self._setNumber(4, value)

    def getNations(self):
        return self._getArray(5)

    def setNations(self, value):
        self._setArray(5, value)

    @staticmethod
    def getNationsType():
        return NationItemInfoViewModel

    def _initialize(self):
        super(ResourceInfoViewModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('balance', 0)
        self._addNumberProperty('limit', 0)
        self._addNumberProperty('rate', 0)
        self._addNumberProperty('percent', 0)
        self._addArrayProperty('nations', Array())
