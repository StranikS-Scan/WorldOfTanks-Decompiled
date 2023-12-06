# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/bonus_group_tooltip.py
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses
from shared_utils import first
from skeletons.gui.game_control import IGuiLootBoxesController
from gui_lootboxes.gui.bonuses.bonuses_packers import getLootBoxesBonusPacker
from gui_lootboxes.gui.bonuses.bonuses_sorter import sortBonuses
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.bonus_group_tooltip_model import BonusGroupTooltipModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.bg_tooltip_row_model import BgTooltipRowModel
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import VEHICLES_BONUS_NAME
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import BonusType
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.gui_helpers import detectBonusType
from gui.server_events.bonuses import splitBonuses
BONUS_GROUP_TOOLTIP_PROCESSORS = []

class BonusGroupTooltip(ViewImpl):
    __slots__ = ('__bonuses', '__bonusGroup')
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, bonusGroup, bonuses, lootBoxCategory):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.BonusGroupTooltip())
        settings.model = BonusGroupTooltipModel()
        super(BonusGroupTooltip, self).__init__(settings)
        self.__bonusGroup = bonusGroup
        self.__bonuses = sortBonuses(bonuses, self.__guiLootBoxes.getBonusesOrder(lootBoxCategory))
        self.__bonuses = aggregateSimilarBonuses(self.__bonuses)
        for processor in BONUS_GROUP_TOOLTIP_PROCESSORS:
            self.__bonuses = processor(self.__bonuses)

    @property
    def viewModel(self):
        return super(BonusGroupTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BonusGroupTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setBonusGroup(self.__bonusGroup)
            self.__fillBonusRows(vm)

    def __fillBonusRows(self, model):
        bonusRowsModel = model.getBonusRows()
        packer = getLootBoxesBonusPacker()
        if first(self.__bonuses).getName() == VEHICLES_BONUS_NAME:
            premiumVehicles, rentedVehicles = self.__splitVehicleGroup(splitBonuses(self.__bonuses))
            if premiumVehicles:
                bonusRowsModel.addViewModel(self.__createBonusRow(premiumVehicles, packer))
            if rentedVehicles:
                bonusRowsModel.addViewModel(self.__createBonusRow(rentedVehicles, packer))
        else:
            for b in self.__bonuses:
                bonusRowsModel.addViewModel(self.__createBonusRow((b,), packer))

        bonusRowsModel.invalidate()

    def __createBonusRow(self, bonuses, packer):
        bonusesRow = BgTooltipRowModel()
        bonusesRow.setBonusType(BonusType(detectBonusType(bonuses)))
        packBonusModelAndTooltipData(bonuses, bonusesRow.getBonuses(), packer=packer)
        return bonusesRow

    def __splitVehicleGroup(self, bonuses):
        premiumVehicles = []
        rentedVehicles = []
        for b in bonuses:
            bonusType = detectBonusType((b,))
            if bonusType == BonusType.VEHICLE:
                premiumVehicles.append(b)
            if bonusType == BonusType.RENTEDVEHICLE:
                rentedVehicles.append(b)

        return (premiumVehicles, rentedVehicles)
