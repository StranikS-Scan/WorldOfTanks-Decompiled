# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/tech_tree_nation_model.py
from frameworks.wulf import ViewModel

class TechTreeNationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TechTreeNationModel, self).__init__(properties=properties, commands=commands)

    def getNationIndex(self):
        return self._getNumber(0)

    def setNationIndex(self, value):
        self._setNumber(0, value)

    def getNation(self):
        return self._getString(1)

    def setNation(self, value):
        self._setString(1, value)

    def getHasNewDiscountEvent(self):
        return self._getBool(2)

    def setHasNewDiscountEvent(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(TechTreeNationModel, self)._initialize()
        self._addNumberProperty('nationIndex', 0)
        self._addStringProperty('nation', '')
        self._addBoolProperty('hasNewDiscountEvent', False)
