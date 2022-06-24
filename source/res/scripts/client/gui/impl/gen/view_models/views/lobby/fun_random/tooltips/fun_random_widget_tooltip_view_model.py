# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/fun_random/tooltips/fun_random_widget_tooltip_view_model.py
from frameworks.wulf import ViewModel

class FunRandomWidgetTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(FunRandomWidgetTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getLeftTime(self):
        return self._getNumber(0)

    def setLeftTime(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(FunRandomWidgetTooltipViewModel, self)._initialize()
        self._addNumberProperty('leftTime', -1)
