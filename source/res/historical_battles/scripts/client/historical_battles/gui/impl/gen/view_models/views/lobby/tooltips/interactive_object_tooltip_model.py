# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/interactive_object_tooltip_model.py
from frameworks.wulf import ViewModel

class InteractiveObjectTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(InteractiveObjectTooltipModel, self).__init__(properties=properties, commands=commands)

    def getItemID(self):
        return self._getNumber(0)

    def setItemID(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(InteractiveObjectTooltipModel, self)._initialize()
        self._addNumberProperty('itemID', 0)
