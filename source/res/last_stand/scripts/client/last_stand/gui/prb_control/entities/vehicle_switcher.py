# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/vehicle_switcher.py
from CurrentVehicle import g_currentVehicle
from last_stand.gui import vehicleComparisonKey
from last_stand.gui.ls_account_settings import getSettings, AccountSettingsKeys, setSettings
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from last_stand_common.last_stand_constants import QUEUE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher

class VehicleSwitcher(object):
    _lsCtrl = dependency.descriptor(ILSController)
    _difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def startSwitcher(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.selectModeVehicle()

    def stopSwitcher(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def selectModeVehicle(self, vehInvID=0):
        if not vehInvID:
            vehInvID = self._getFavoriteVehInvID()
        if vehInvID:
            setSettings(AccountSettingsKeys.FAVORITES_VEHICLE, vehInvID)
            g_currentVehicle.selectVehicle(vehInvID)
        else:
            g_currentVehicle.selectNoVehicle()

    @property
    def __currentQueueType(self):
        return self._difficultyLevelCtrl.getCurrentQueueType()

    def _getFavoriteVehInvID(self):
        vehInvID = getSettings(AccountSettingsKeys.FAVORITES_VEHICLE)
        if vehInvID and self._itemsCache.items.getVehicle(vehInvID) is None:
            vehInvID = None
        if not vehInvID:
            vehicles = sorted(self._lsCtrl.getSuitableVehicles(), key=vehicleComparisonKey)
            if vehicles:
                vehInvID = vehicles[0].invID
        return vehInvID

    def __onCurrentVehicleChanged(self):
        g_eventDispatcher.updateUI()
