# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/vehicle_switcher.py
from __future__ import absolute_import
from functools import partial
import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from halloween.gui.halloween_account_settings import getSettings, AccountSettingsKeys, setSettings
from halloween.gui.shared.event_dispatcher import isViewLoaded
from halloween.skeletons.halloween_controller import IHalloweenController
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class VehicleSwitcher(object):
    _halloweenCtrl = dependency.descriptor(IHalloweenController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def startSwitcher(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.selectVehicleWithWaiting()

    def stopSwitcher(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def selectModeVehicle(self, vehInvID=0):
        if not vehInvID:
            vehInvID = self._getFavoriteVehInvID()
        setSettings(AccountSettingsKeys.FAVORITES_VEHICLE, vehInvID)
        g_currentVehicle.selectVehicle(vehInvID)

    def selectVehicleWithWaiting(self, vehInvID=0):
        if isViewLoaded(R.views.halloween.mono.lobby.hangar()):
            self.selectModeVehicle(vehInvID)
        else:
            BigWorld.callback(0.1, partial(self.selectVehicleWithWaiting, vehInvID))

    def _getFavoriteVehInvID(self):
        vehInvID = getSettings(AccountSettingsKeys.FAVORITES_VEHICLE)
        if not vehInvID:
            vehicles = self._halloweenCtrl.getConfig().get('vehicles', [])
            vehicle = self._itemsCache.items.getItemByCD(vehicles[0] if vehicles else 0)
            vehInvID = vehicle.invID if vehicle and vehicle.isInInventory else 0
        return vehInvID

    def __onCurrentVehicleChanged(self):
        if g_currentVehicle.item is None:
            return
        else:
            vehicles = self._halloweenCtrl.getConfig().get('vehicles', [])
            if g_currentVehicle.item.intCD not in vehicles:
                g_currentVehicle.selectVehicle(self._getFavoriteVehInvID())
            return
