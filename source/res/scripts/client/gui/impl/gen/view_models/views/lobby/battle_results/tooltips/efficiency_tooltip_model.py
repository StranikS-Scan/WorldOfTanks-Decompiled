# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/tooltips/efficiency_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_item_model import EfficiencyItemModel

class EfficiencyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(EfficiencyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def getDetails(self):
        return self._getArray(3)

    def setDetails(self, value):
        self._setArray(3, value)

    @staticmethod
    def getDetailsType():
        return EfficiencyItemModel

    def getStatuses(self):
        return self._getArray(4)

    def setStatuses(self, value):
        self._setArray(4, value)

    @staticmethod
    def getStatusesType():
        return int

    def _initialize(self):
        super(EfficiencyTooltipModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addArrayProperty('details', Array())
        self._addArrayProperty('statuses', Array())
