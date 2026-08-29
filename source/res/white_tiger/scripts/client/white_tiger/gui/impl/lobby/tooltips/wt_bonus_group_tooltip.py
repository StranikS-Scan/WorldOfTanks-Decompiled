# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_bonus_group_tooltip.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses
from skeletons.gui.game_control import IGuiLootBoxesController
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_bonus_group_tooltip_model import WtBonusGroupTooltipModel
from gui_lootboxes.gui.bonuses.bonuses_packers import getLootBoxesBonusPacker
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses
BONUS_GROUP_TOOLTIP_PROCESSORS = []

class WtBonusGroupTooltip(ViewImpl):
    __slots__ = ('__bonuses', '__bonusGroup')
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, bonusGroup, bonuses, lootBoxCategory):
        settings = ViewSettings(R.views.white_tiger.lobby.tooltips.WtBonusGroupTooltip())
        settings.model = WtBonusGroupTooltipModel()
        super(WtBonusGroupTooltip, self).__init__(settings)
        self.__bonusGroup = bonusGroup
        self.__bonuses = sortBonuses(bonuses, self.__guiLootBoxes.getBonusesOrder(lootBoxCategory))
        self.__bonuses = aggregateSimilarBonuses(self.__bonuses)
        for processor in BONUS_GROUP_TOOLTIP_PROCESSORS:
            self.__bonuses = processor(self.__bonuses)

    @property
    def viewModel(self):
        return super(WtBonusGroupTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtBonusGroupTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setBonusGroup(self.__bonusGroup)
            self.__fillBonuses(vm)

    def __fillBonuses(self, model):
        packer = getLootBoxesBonusPacker()
        packBonusModelAndTooltipData(self.__bonuses, model.getBonuses(), packer=packer)
