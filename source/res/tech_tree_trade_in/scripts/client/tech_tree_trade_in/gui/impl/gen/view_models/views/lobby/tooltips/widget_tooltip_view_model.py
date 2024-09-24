# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/tooltips/widget_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WidgetTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WidgetTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getDateEnd(self):
        return self._getNumber(0)

    def setDateEnd(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(WidgetTooltipViewModel, self)._initialize()
        self._addNumberProperty('dateEnd', 0)
