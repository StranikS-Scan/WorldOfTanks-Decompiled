# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/ranked_efficiency_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.ranked_season_efficiency_model import RankedSeasonEfficiencyModel

class RankedEfficiencyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RankedEfficiencyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return RankedSeasonEfficiencyModel

    def _initialize(self):
        super(RankedEfficiencyTooltipModel, self)._initialize()
        self._addArrayProperty('items', Array())
