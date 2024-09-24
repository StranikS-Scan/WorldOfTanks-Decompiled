# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/tooltips/widget_tooltip_view.py
from frameworks.wulf import ViewSettings
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tooltips.widget_tooltip_view_model import WidgetTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class WidgetTooltipView(ViewImpl):
    __slots__ = ('_dateEnd',)

    def __init__(self, dateEnd):
        settings = ViewSettings(R.views.tech_tree_trade_in.lobby.tooltips.WidgetTooltipView())
        settings.model = WidgetTooltipViewModel()
        self._dateEnd = dateEnd
        super(WidgetTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WidgetTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        if self._dateEnd is None:
            return
        else:
            self.viewModel.setDateEnd(self._dateEnd)
            return
