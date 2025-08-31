# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_event_battles_end_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WtEventBattlesEndTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEventBattlesEndTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getNumber(0)

    def setEndDate(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(WtEventBattlesEndTooltipViewModel, self)._initialize()
        self._addNumberProperty('endDate', -1)
