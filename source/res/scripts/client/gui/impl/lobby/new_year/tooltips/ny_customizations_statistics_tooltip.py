# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_customizations_statistics_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.rewards_helper import getVehByStyleCD
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_statistics_reward_model import Type
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_customizations_statistics_tooltip_model import NyCustomizationsStatisticsTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_loot_box_statistics_customization_model import NyLootBoxStatisticsCustomizationModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxStatisticsKey
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class NyCustomizationsStatisticsTooltip(ViewImpl):
    __slots__ = ('__lootboxID',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __c11n = dependency.descriptor(ICustomizationService)

    def __init__(self, lootboxID, layoutID=R.views.lobby.new_year.tooltips.NyCustomizationsStatisticsTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = NyCustomizationsStatisticsTooltipModel()
        super(NyCustomizationsStatisticsTooltip, self).__init__(settings)
        self.__lootboxID = lootboxID

    @property
    def viewModel(self):
        return super(NyCustomizationsStatisticsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            modelCustomizations = model.getCustomizations()
            statsKey = getLootboxStatisticsKey(self.__lootboxID)
            if statsKey is not None:
                lootboxStats = self.__itemsCache.items.tokens.getLootBoxesStats().get(statsKey)
                if lootboxStats is not None:
                    lootboxRewards, _ = lootboxStats
                    for customizationsData in lootboxRewards.get(Type.CUSTOMIZATIONS.value, {}):
                        if 'compensatedNumber' in customizationsData or customizationsData['custType'] != 'style':
                            continue
                        style = self.__c11n.getItemByID(GUI_ITEM_TYPE.STYLE, customizationsData['id'])
                        vehicle = getVehByStyleCD(style.intCD)
                        customizationModel = NyLootBoxStatisticsCustomizationModel()
                        customizationModel.setName(style.userName)
                        customizationModel.setLongName(vehicle.userName)
                        customizationModel.setTier(vehicle.level)
                        customizationModel.setTankType(vehicle.type)
                        modelCustomizations.addViewModel(customizationModel)

            modelCustomizations.invalidate()
        return
