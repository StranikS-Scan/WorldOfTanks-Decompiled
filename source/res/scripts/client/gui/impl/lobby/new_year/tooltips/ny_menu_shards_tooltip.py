# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_menu_shards_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_menu_shards_tooltip_model import NyMenuShardsTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NyMenuShardsTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.new_year.tooltips.NyMenuShardsTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = NyMenuShardsTooltipModel()
        super(NyMenuShardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMenuShardsTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(NyMenuShardsTooltip, self)._initialize()
        self.viewModel.setShardsCount(dependency.instance(IItemsCache).items.festivity.getShardsCount())
