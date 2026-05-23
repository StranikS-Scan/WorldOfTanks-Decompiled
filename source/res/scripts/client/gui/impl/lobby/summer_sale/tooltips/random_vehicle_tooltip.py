# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/summer_sale/tooltips/random_vehicle_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.summer_sale.random_vehicle_tooltip_model import RandomVehicleTooltipModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.loot_box.loot_box_helper import aggregateSimilarBonuses
from gui.impl.lobby.promo_code_reward_screen.bonuses_sorter import sortBonuses
from gui.impl.pub import ViewImpl
from gui.summer_sale.bonus_packers import getSummerSaleRewardsBonusPacker
from helpers import dependency
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.shared import IItemsCache

class RandomVehicleTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __slots__ = ('__lootBox', '__bonuses')

    def __init__(self, lootBoxID):
        settings = ViewSettings(R.views.lobby.summer_sale.RandomVehicleTooltip())
        settings.flags = ViewFlags.VIEW
        settings.model = RandomVehicleTooltipModel()
        super(RandomVehicleTooltip, self).__init__(settings)
        self.__lootBox = self.__itemsCache.items.tokens.getLootBoxByID(lootBoxID)
        bonuses = self.__lootBox.getBonusesByGroup('vehicle')
        self.__bonuses = aggregateSimilarBonuses(sortBonuses(bonuses, self.__guiLootBoxes.getBonusesOrder(self.__lootBox.getCategory())))

    @property
    def viewModel(self):
        return super(RandomVehicleTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.getViewModel().transaction() as tx:
            vehiclesBonusModel = tx.getVehicles()
            vehiclesBonusModel.clear()
            packBonusModelAndTooltipData(self.__bonuses, vehiclesBonusModel, packer=getSummerSaleRewardsBonusPacker())
            vehiclesBonusModel.invalidate()
