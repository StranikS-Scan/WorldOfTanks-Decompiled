# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_lootboxes_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_lootboxes_tooltip_view_model import WtEventLootboxesTooltipViewModel
from gui.impl.pub import ViewImpl

class WtEventLootBoxesTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventLootBoxesTooltipView())
        settings.model = WtEventLootboxesTooltipViewModel()
        super(WtEventLootBoxesTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()
