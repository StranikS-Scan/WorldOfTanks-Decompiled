# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/param_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.param_tooltip_model import ParamTooltipModel
from gui.impl.pub import ViewImpl

class ParamTooltipView(ViewImpl):

    def __init__(self, tooltipType, params, resId):
        settings = ViewSettings(layoutID=resId, model=ParamTooltipModel())
        self._tooltipType = tooltipType
        self._params = params
        super(ParamTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ParamTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ParamTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setType(self._tooltipType)
            model.setParams(self._params)
