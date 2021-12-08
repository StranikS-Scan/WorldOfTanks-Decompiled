# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_vehicles_statistics_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_statistics_reward_model import Type
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_loot_box_statistics_vehicle_model import NyLootBoxStatisticsVehicleModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_vehicles_statistics_tooltip_model import NyVehiclesStatisticsTooltipModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxStatisticsKey
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NyVehiclesStatisticsTooltip(ViewImpl):
    __slots__ = ('__lootboxID',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, lootboxID, layoutID=R.views.lobby.new_year.tooltips.NyVehiclesStatisticsTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = NyVehiclesStatisticsTooltipModel()
        super(NyVehiclesStatisticsTooltip, self).__init__(settings)
        self.__lootboxID = lootboxID

    @property
    def viewModel(self):
        return super(NyVehiclesStatisticsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            compensatedCount = 0
            vehicles = []
            statsKey = getLootboxStatisticsKey(self.__lootboxID)
            if statsKey is not None:
                lootboxStats = self.__itemsCache.items.tokens.getLootBoxesStats().get(statsKey)
                if lootboxStats is not None:
                    lootboxRewards, _ = lootboxStats
                    for vehiclesData in lootboxRewards.get(Type.VEHICLES.value, {}):
                        for vehicleCD, compensationData in vehiclesData.iteritems():
                            compensatedNumber = compensationData.get('compensatedNumber')
                            if compensatedNumber is not None:
                                compensatedCount += compensatedNumber
                            vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
                            vehicles.append(vehicle)

            vehicles.sort(key=lambda v: v.level, reverse=True)
            model.setCount(compensatedCount)
            modelVehicles = model.getVehicles()
            for vehicle in vehicles:
                vehicleModel = NyLootBoxStatisticsVehicleModel()
                vehicleModel.setLongName(vehicle.userName)
                vehicleModel.setTier(vehicle.level)
                vehicleModel.setTankType(vehicle.type)
                modelVehicles.addViewModel(vehicleModel)

            modelVehicles.invalidate()
        return
