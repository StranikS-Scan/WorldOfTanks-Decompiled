# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_event_stamp_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WtEventStampTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEventStampTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getStampsPerProgressionStage(self):
        return self._getNumber(0)

    def setStampsPerProgressionStage(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(WtEventStampTooltipViewModel, self)._initialize()
        self._addNumberProperty('stampsPerProgressionStage', 0)
