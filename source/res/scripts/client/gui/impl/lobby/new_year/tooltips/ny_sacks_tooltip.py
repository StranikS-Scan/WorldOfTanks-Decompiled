# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_sacks_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_sacks_tooltip_model import NySacksTooltipModel
from gui.impl.pub import ViewImpl

class NySacksTooltip(ViewImpl):
    __slots__ = ('__bundleType',)

    def __init__(self, bundleType, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NySacksTooltip())
        settings.model = NySacksTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NySacksTooltip, self).__init__(settings)
        self.__bundleType = bundleType

    @property
    def viewModel(self):
        return super(NySacksTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NySacksTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setBundleType(self.__bundleType)
