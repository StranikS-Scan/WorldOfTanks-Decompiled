# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_lootbox_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view_model import WtEventLootboxTooltipViewModel
from gui.impl.pub import ViewImpl

class WtEventLootboxTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventLootboxTooltipView())
        settings.model = WtEventLootboxTooltipViewModel()
        super(WtEventLootboxTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventLootboxTooltipView, self).getViewModel()
