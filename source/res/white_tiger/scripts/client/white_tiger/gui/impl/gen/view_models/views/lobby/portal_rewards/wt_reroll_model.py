# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portal_rewards/wt_reroll_model.py
from frameworks.wulf import ViewModel

class WtRerollModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(WtRerollModel, self).__init__(properties=properties, commands=commands)

    def getIsAffordable(self):
        return self._getBool(0)

    def setIsAffordable(self, value):
        self._setBool(0, value)

    def getCurrency(self):
        return self._getString(1)

    def setCurrency(self, value):
        self._setString(1, value)

    def getPrice(self):
        return self._getNumber(2)

    def setPrice(self, value):
        self._setNumber(2, value)

    def getCount(self):
        return self._getNumber(3)

    def setCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(WtRerollModel, self)._initialize()
        self._addBoolProperty('isAffordable', False)
        self._addStringProperty('currency', 'gold')
        self._addNumberProperty('price', 400)
        self._addNumberProperty('count', 2)
