# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/battle_result/player_results/stat_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class StatItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(StatItemModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getWreathImage(self):
        return self._getResource(1)

    def setWreathImage(self, value):
        self._setResource(1, value)

    def getValue(self):
        return self._getNumber(2)

    def setValue(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(StatItemModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addResourceProperty('wreathImage', R.invalid())
        self._addNumberProperty('value', -1)
