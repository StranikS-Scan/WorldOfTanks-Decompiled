# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_shards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_shards_tooltip_model import NyShardsTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NyShardsTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.new_year.tooltips.NyShardsTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = NyShardsTooltipModel()
        super(NyShardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyShardsTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NyShardsTooltip, self)._initialize()
        self.viewModel.setShardsCount(dependency.instance(IItemsCache).items.festivity.getShardsCount())
