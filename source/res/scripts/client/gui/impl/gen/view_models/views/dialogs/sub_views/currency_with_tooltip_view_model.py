# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/currency_with_tooltip_view_model.py
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencyViewModel

class CurrencyWithTooltipViewModel(CurrencyViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(CurrencyWithTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getDiscountTooltipContentId(self):
        return self._getNumber(7)

    def setDiscountTooltipContentId(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(CurrencyWithTooltipViewModel, self)._initialize()
        self._addNumberProperty('discountTooltipContentId', 0)
