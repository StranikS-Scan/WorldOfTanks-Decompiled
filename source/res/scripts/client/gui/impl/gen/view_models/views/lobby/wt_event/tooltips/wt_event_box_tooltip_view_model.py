# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_box_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class WtEventBoxTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(WtEventBoxTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getBoxType(self):
        return self._getString(0)

    def setBoxType(self, value):
        self._setString(0, value)

    def getGold(self):
        return self._getNumber(1)

    def setGold(self, value):
        self._setNumber(1, value)

    def getHasCollectionItem(self):
        return self._getBool(2)

    def setHasCollectionItem(self, value):
        self._setBool(2, value)

    def getVehicles(self):
        return self._getString(3)

    def setVehicles(self, value):
        self._setString(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(WtEventBoxTooltipViewModel, self)._initialize()
        self._addStringProperty('boxType', '')
        self._addNumberProperty('gold', 0)
        self._addBoolProperty('hasCollectionItem', False)
        self._addStringProperty('vehicles', '')
        self._addArrayProperty('rewards', Array())
