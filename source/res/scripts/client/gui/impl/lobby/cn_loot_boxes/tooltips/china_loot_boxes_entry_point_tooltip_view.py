# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/tooltips/china_loot_boxes_entry_point_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.tooltips.entry_point_model import EntryPointModel
from gui.impl.pub import ViewImpl

class ChinaLootBoxesEntryPointTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxesEntryPointTooltipView())
        settings.model = EntryPointModel()
        super(ChinaLootBoxesEntryPointTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChinaLootBoxesEntryPointTooltipView, self).getViewModel()
