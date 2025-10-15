# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/params_tooltip.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.params_tooltip_model import ParamsTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class ParamsTooltip(ViewImpl):
    __slots__ = ('__name',)

    def __init__(self, name):
        settings = ViewSettings(R.views.portal.lobby.tooltips.ParamsTooltip())
        settings.model = ParamsTooltipModel()
        self.__name = name
        super(ParamsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ParamsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ParamsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setName(self.__name)
