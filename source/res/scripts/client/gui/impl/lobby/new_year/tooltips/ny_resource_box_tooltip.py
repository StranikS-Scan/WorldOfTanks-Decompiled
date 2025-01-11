# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_resource_box_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_box_tooltip_model import NyResourceBoxTooltipModel
from gui.impl.pub import ViewImpl

class NyResourceBoxTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyResourceBoxTooltip())
        settings.model = NyResourceBoxTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyResourceBoxTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourceBoxTooltip, self).getViewModel()

    def _onLoading(self, isFriendsList, *args, **kwargs):
        super(NyResourceBoxTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setIsFriendsList(isFriendsList)
