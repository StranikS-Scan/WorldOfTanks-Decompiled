# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/tab_tooltip_view.py
from frameworks.wulf import ViewSettings
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.tab_tooltip_view_model import TabTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class TabTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, tabId=None):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.TabTooltipView())
        settings.model = TabTooltipViewModel()
        super(TabTooltipView, self).__init__(settings)
        self.viewModel.setTabId(tabId)

    @property
    def viewModel(self):
        return super(TabTooltipView, self).getViewModel()
