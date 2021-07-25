# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/crew_retrain_penalty_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.crew_retrain_penalty_item import CrewRetrainPenaltyItem

class CrewRetrainPenaltyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CrewRetrainPenaltyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTotal(self):
        return self._getNumber(0)

    def setTotal(self, value):
        self._setNumber(0, value)

    def getItems(self):
        return self._getArray(1)

    def setItems(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(CrewRetrainPenaltyTooltipModel, self)._initialize()
        self._addNumberProperty('total', 0)
        self._addArrayProperty('items', Array())
