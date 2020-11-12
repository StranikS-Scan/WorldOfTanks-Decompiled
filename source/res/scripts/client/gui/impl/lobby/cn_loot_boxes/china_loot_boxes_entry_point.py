# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/cn_loot_boxes/china_loot_boxes_entry_point.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CN_VIEWED_BOXES_COUNT
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.cn_loot_boxes.china_loot_boxes_entry_point_model import ChinaLootBoxesEntryPointModel
from gui.impl.lobby.cn_loot_boxes.tooltips.china_loot_boxes_entry_point_tooltip_view import ChinaLootBoxesEntryPointTooltipView
from gui.impl.lobby.cn_loot_boxes.china_loot_boxes_popover import ChinaLootBoxesPopover
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import ICNLootBoxesController

class ChinaLootBoxesEntryPointWidget(ViewImpl):
    __cnLootBoxesCtrl = dependency.descriptor(ICNLootBoxesController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.cn_loot_boxes.china_loot_boxes_entry_point_view.ChinaLootBoxesEntryPointView(), ViewFlags.COMPONENT, ChinaLootBoxesEntryPointModel())
        super(ChinaLootBoxesEntryPointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChinaLootBoxesEntryPointWidget, self).getViewModel()

    def createPopOverContent(self, event):
        return ChinaLootBoxesPopover()

    def createToolTipContent(self, event, contentID):
        return ChinaLootBoxesEntryPointTooltipView() if contentID == R.views.lobby.cn_loot_boxes.tooltips.ChinaLootBoxesEntryPointTooltipView() else None

    def _initialize(self):
        super(ChinaLootBoxesEntryPointWidget, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self.__cnLootBoxesCtrl.onBoxesCountChange += self.__updateBoxesCount

    def _onLoading(self, *args, **kwargs):
        super(ChinaLootBoxesEntryPointWidget, self)._onLoading(*args, **kwargs)
        self.__updateBoxesCount(self.__cnLootBoxesCtrl.getBoxesCount())

    def _finalize(self):
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self.__cnLootBoxesCtrl.onBoxesCountChange -= self.__updateBoxesCount
        super(ChinaLootBoxesEntryPointWidget, self)._finalize()

    def __onWidgetClick(self):
        self.viewModel.setHasNew(False)
        AccountSettings.setSettings(CN_VIEWED_BOXES_COUNT, self.__cnLootBoxesCtrl.getBoxesCount())

    def __updateBoxesCount(self, count):
        lastViewed = AccountSettings.getSettings(CN_VIEWED_BOXES_COUNT)
        with self.viewModel.transaction() as model:
            model.setBoxesCount(count)
            model.setHasNew(count > lastViewed)
