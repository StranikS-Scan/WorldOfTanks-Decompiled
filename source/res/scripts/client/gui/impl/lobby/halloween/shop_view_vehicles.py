# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/shop_view_vehicles.py
import itertools
from gui.impl.gen import R
from constants import EVENT
from gui.impl.lobby.halloween.shop_view import ShopView, BonusGroups
from gui.impl.gen.view_models.views.lobby.halloween.shop_view_model import PageTypeEnum
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.impl.gen.view_models.views.lobby.halloween.tank_model import TankModel
from gui.impl.lobby.halloween.tooltips.shop_vehicle_tooltip import ShopVehicleTooltip
from gui.server_events.bonuses import mergeBonuses
from gui.shared.utils.functions import replaceHyphenToUnderscore

class ShopViewVehicles(ShopView):
    PAGE_TYPE = PageTypeEnum.VEHICLES
    SHOP_TYPE_NAME = EVENT.SHOP.TYPE.VEHICLES
    BONUS_GROUPS = (BonusGroups.PREMIUM, BonusGroups.VEHICLES, BonusGroups.SLOTS)
    BONUS_GROUPS_ORDER = (BonusGroups.PREMIUM, BonusGroups.VEHICLES, BonusGroups.OTHER)

    def __init__(self, layoutID):
        self._previewVehicleIntCD = g_currentPreviewVehicle.item.intCD if g_currentPreviewVehicle.isPresent() else None
        super(ShopViewVehicles, self).__init__(layoutID)
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.halloween.tooltips.ShopVehicleTooltip():
            tankId = event.getArgument('tankId')
            return ShopVehicleTooltip(tankId)

    def _finalize(self):
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onInventoryChanged
        super(ShopViewVehicles, self)._finalize()

    def _onLoading(self):
        super(ShopViewVehicles, self)._onLoading()
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onInventoryChanged

    def _getBundlesAndBonuses(self):
        bundlesAndBonuses = super(ShopViewVehicles, self)._getBundlesAndBonuses()
        return [ (bundle, bonuses) for bundle, bonuses in bundlesAndBonuses if self.__hasPreviewVehicleInBonuses(bonuses) ]

    def _fillBonusesGroup(self, model, groupName, bonuses):
        if groupName == BonusGroups.VEHICLES:
            self.__fillVehicles(model, bonuses)
            return
        super(ShopViewVehicles, self)._fillBonusesGroup(model, groupName, bonuses)

    def __fillVehicles(self, vehiclesModel, bonuses):
        vehiclesModel.clear()
        bonuses = mergeBonuses(bonuses)
        vehicles = bonuses[0].getVehicles()
        vehicles.sort(key=lambda (v, _): v.intCD != self._previewVehicleIntCD)
        for veh, _ in vehicles:
            vehicle = self.itemsCache.items.getItemByCD(veh.intCD)
            if vehicle.isInInventory:
                continue
            tankModel = TankModel()
            tankModel.setId(veh.intCD)
            tankModel.setName(vehicle.userName)
            tankModel.setType(vehicle.type)
            tankModel.setIconName(replaceHyphenToUnderscore(vehicle.name.replace(':', '-')))
            vehiclesModel.addViewModel(tankModel)

        vehiclesModel.invalidate()

    def __hasPreviewVehicleInBonuses(self, bonuses):
        vehicleBonuses = itertools.chain.from_iterable((bonus.getVehicles() for bonus in bonuses if bonus.getName() == 'vehicles'))
        return any((True for veh, _ in vehicleBonuses if veh.intCD == self._previewVehicleIntCD))

    def __onInventoryChanged(self):
        if self._previewVehicleIntCD is None:
            return
        else:
            vehicle = self.itemsCache.items.getItemByCD(self._previewVehicleIntCD)
            if vehicle.isInInventory and vehicle.isOnlyForEventBattles:
                g_currentVehicle.selectEventVehicle(vehicle.invID)
            self.close()
            return
