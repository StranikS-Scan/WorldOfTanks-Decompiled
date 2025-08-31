# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/util/vehicle.py
from web.client_web_api.api import C2WHandler, c2w
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

class VehicleCompareEventHandler(C2WHandler):
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def init(self):
        super(VehicleCompareEventHandler, self).init()
        self.__comparisonBasket.onChange += self.__onComparisonBasketChange

    def fini(self):
        self.__comparisonBasket.onChange -= self.__onComparisonBasketChange
        super(VehicleCompareEventHandler, self).fini()

    @c2w(name='comparison_basket_update')
    def __onComparisonBasketChange(self, *args, **kwargs):
        return {'basketContents': self.__comparisonBasket.getVehiclesCDs(),
         'basketMaxCount': self.__comparisonBasket.maxVehiclesToCompare}


class VehicleStateEventHandler(C2WHandler):
    __itemsCache = dependency.descriptor(IItemsCache)

    def init(self):
        super(VehicleStateEventHandler, self).init()
        self.__itemsCache.onSyncCompleted += self.__onVehicleStateChanged

    def fini(self):
        self.__itemsCache.onSyncCompleted -= self.__onVehicleStateChanged
        super(VehicleStateEventHandler, self).fini()

    def __onVehicleStateChanged(self, reason, diff):
        updateReasons = {CACHE_SYNC_REASON.CLIENT_UPDATE, CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC}
        if reason in updateReasons and GUI_ITEM_TYPE.VEHICLE in diff:
            vehicleCDs = diff[GUI_ITEM_TYPE.VEHICLE]
            for vehicleCD in vehicleCDs:
                self.__sendVehicleState(vehicleCD)

    @c2w(name='vehicle_state_update')
    def __sendVehicleState(self, vehicleCD):
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        state, stateLevel = vehicle.getState()
        return {'id': vehicleCD,
         'state': state,
         'level': stateLevel}
