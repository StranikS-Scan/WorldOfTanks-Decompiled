# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/deadline_tooltip.py
from constants import VERY_BIG_TIME
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.deadline_tooltip_model import DeadlineTooltipModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.short_statistic_lootboxes import ShortStatisticLootboxes
from gui_lootboxes.skeletons.statistic_lootbox_controller import IStatisticLootBoxController
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class DeadlineTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __statisticCtrl = dependency.descriptor(IStatisticLootBoxController)

    def __init__(self):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.DeadlineTooltip())
        settings.model = DeadlineTooltipModel()
        super(DeadlineTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DeadlineTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__fillModel()
        super(DeadlineTooltip, self)._onLoading()

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            statistic = self.__statisticCtrl.getLootboxesExpireInfo()
            lootBoxesArray = model.getLootboxes()
            lootBoxesArray.clear()
            for lootboxID, expireDate in statistic.iteritems():
                shortStatisticLootbox = ShortStatisticLootboxes()
                lootBox = self.__itemsCache.items.tokens.getLootBoxByID(lootboxID)
                if lootBox is not None:
                    shortStatisticLootbox.setId(lootboxID)
                    shortStatisticLootbox.setDate(expireDate if expireDate < VERY_BIG_TIME else 0)
                    shortStatisticLootbox.setName(lootBox.getUserName())
                    shortStatisticLootbox.setType(lootBox.getType())
                    lootBoxesArray.addViewModel(shortStatisticLootbox)

            lootBoxesArray.invalidate()
        return
