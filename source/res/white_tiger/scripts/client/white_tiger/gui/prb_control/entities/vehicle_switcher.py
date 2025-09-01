# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/vehicle_switcher.py
import logging
from CurrentVehicle import g_currentVehicle
from white_tiger.gui.white_tiger_account_settings import getWTFavorites, setWTFavorites
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger_common.wt_constants import WT_FIRST_TIME_EVENT_ENTER_TANK
from helpers import dependency
from items.vehicles import makeVehicleTypeCompDescrByName
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class WhiteTigerVehicleSwitcher(object):
    _wtCtrl = dependency.descriptor(IWhiteTigerController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def startSwitcher(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.selectModeVehicle()

    def stopSwitcher(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def selectModeVehicle(self, vehInvID=0):
        if not vehInvID:
            vehInvID = self._getFavoriteVehInvID()
        setWTFavorites(vehInvID)
        g_currentVehicle.selectVehicle(vehInvID)

    def _getFavoriteVehInvID(self):
        vehInvID = getWTFavorites()
        vehicle = self._itemsCache.items.getVehicle(vehInvID)
        if vehicle and vehicle.intCD in self._wtCtrl.getWTVehicles():
            return vehInvID
        firstVehicleCD = makeVehicleTypeCompDescrByName(WT_FIRST_TIME_EVENT_ENTER_TANK)
        vehicle = self._itemsCache.items.getItemByCD(firstVehicleCD)
        vehInvID = vehicle.invID if vehicle and vehicle.isInInventory else 0
        if vehInvID == 0:
            _logger.error('WT vehicle %d has not been found in inventory', firstVehicleCD)
        setWTFavorites(vehInvID)
        return vehInvID

    def __onCurrentVehicleChanged(self):
        if g_currentVehicle.item is None:
            return
        else:
            vehicles = self._wtCtrl.getWTVehicles()
            if g_currentVehicle.item.intCD not in vehicles:
                g_currentVehicle.selectVehicle(self._getFavoriteVehInvID())
            return
