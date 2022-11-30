# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_random_resource_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_random_resource_tooltip_model import NyRandomResourceTooltipModel
from gui.impl.pub import ViewImpl

class NyRandomResourceTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyRandomResourceTooltip())
        settings.model = NyRandomResourceTooltipModel()
        settings.args = args
        super(NyRandomResourceTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyRandomResourceTooltip, self).getViewModel()

    def _onLoading(self, resourceValue, isShownFromStore):
        super(NyRandomResourceTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setResourceValue(resourceValue)
            model.setIsShownFromStore(isShownFromStore)
