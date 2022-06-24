# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/frontline/dialogs/blank_price_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.frontline.blank_price_view_model import BlankPriceViewModel
from gui.impl.pub import ViewImpl

class BlankPriceView(ViewImpl):
    __slots__ = ('__count',)
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.frontline.dialogs.BlankPrice

    def __init__(self, count, layoutID=None):
        settings = ViewSettings(layoutID or self._LAYOUT_DYN_ACCESSOR())
        settings.model = BlankPriceViewModel()
        self.__count = count
        super(BlankPriceView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(BlankPriceView, self)._onLoading(*args, **kwargs)
        self.getViewModel().setCount(self.__count)
