# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_equipments_statistics_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxStatisticsKey
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_equipment_statistics_model import NyEquipmentStatisticsModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_equipments_statistics_tooltip_model import NyEquipmentsStatisticsTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.shared import IItemsCache
from items.vehicles import getItemByCompactDescr
from helpers import dependency

class NyEquipmentsStatisticsTooltip(ViewImpl):
    __slots__ = ('__rewardKitID',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, rewardKitID):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyEquipmentsStatisticsTooltip())
        settings.model = NyEquipmentsStatisticsTooltipModel()
        self.__rewardKitID = rewardKitID
        super(NyEquipmentsStatisticsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyEquipmentsStatisticsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyEquipmentsStatisticsTooltip, self)._onLoading()
        equipmentsStat = self.__getEquipmentStat()
        with self.viewModel.transaction() as model:
            equipments = model.getEquipments()
            equipments.clear()
            for item in equipmentsStat:
                equipment = NyEquipmentStatisticsModel()
                equipment.setEquipmentName(item['equipmentName'])
                equipment.setCount(item['count'])
                equipment.setTier(item['tier'])
                equipments.addViewModel(equipment)

            equipments.invalidate()

    def __getEquipmentStat(self):
        equipments = []
        statsKey = getLootboxStatisticsKey(self.__rewardKitID)
        if statsKey is not None:
            rewardKitStats = self.__itemsCache.items.tokens.getLootBoxesStats().get(statsKey)
            if rewardKitStats is not None:
                rewardKitRewards, _ = rewardKitStats
                items = rewardKitRewards.get('items', {})
                for item in items:
                    if getItemByCompactDescr(item).isModernized:
                        modernizedItem = getItemByCompactDescr(item)
                        equipments.append({'equipmentName': modernizedItem.iconName,
                         'count': items.get(item, 0),
                         'tier': modernizedItem.level})

        return equipments
