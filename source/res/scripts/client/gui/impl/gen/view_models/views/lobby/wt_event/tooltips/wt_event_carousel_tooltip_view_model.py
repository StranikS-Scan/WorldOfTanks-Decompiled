# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_carousel_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WtEventCarouselTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEventCarouselTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getQuantity(self):
        return self._getNumber(0)

    def setQuantity(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(WtEventCarouselTooltipViewModel, self)._initialize()
        self._addNumberProperty('quantity', 0)
