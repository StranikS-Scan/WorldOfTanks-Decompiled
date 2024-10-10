# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_lootboxes_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_lootboxes_tooltip_view_model import WtLootboxesTooltipViewModel
from gui.impl.pub import ViewImpl

class WtLootBoxesTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.white_tiger.lobby.tooltips.LootBoxesTooltipView())
        settings.model = WtLootboxesTooltipViewModel()
        super(WtLootBoxesTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()
