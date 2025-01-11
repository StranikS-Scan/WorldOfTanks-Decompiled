# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/levelup_price_model.py
from frameworks.wulf import ViewModel

class LevelupPriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(LevelupPriceModel, self).__init__(properties=properties, commands=commands)

    def getCurrency(self):
        return self._getString(0)

    def setCurrency(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def getIsEnough(self):
        return self._getBool(2)

    def setIsEnough(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(LevelupPriceModel, self)._initialize()
        self._addStringProperty('currency', '')
        self._addNumberProperty('value', 0)
        self._addBoolProperty('isEnough', True)
