# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/portal.py
import typing
from account_helpers.account_data_cache import AccountDataStorage
from portal_common.portal_constants import PDATA_KEY_PORTAL_BATTLES
if typing.TYPE_CHECKING:
    from typing import Dict

class Portal(object):

    def __init__(self):
        self.__accountDataCache = AccountDataStorage(PDATA_KEY_PORTAL_BATTLES, onAccountDataChangeCallback=self.__onAccountDataChanged)

    def clear(self):
        self.__accountDataCache.clear()

    @property
    def _data(self):
        return self.__accountDataCache.accountData

    def getVehicleUpgradeTree(self, vehicle):
        return self.__accountDataCache.accountData['vehicleUpgradesMask'].get(vehicle.intCD, 0)

    def getVehicleExperience(self, vehicle):
        return self.__accountDataCache.accountData['vehicleExperience'].get(vehicle.intCD, {}).get('exp', 0)

    def synchronize(self, isFullSync, diff):
        if self.__accountDataCache.isSynchronizationNeeded(diff):
            self.__accountDataCache.synchronize(isFullSync, diff)

    def __onAccountDataChanged(self, accountData):
        pass
