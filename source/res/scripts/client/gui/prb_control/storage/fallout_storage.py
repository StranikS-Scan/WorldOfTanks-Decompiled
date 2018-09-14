# Embedded file name: scripts/client/gui/prb_control/storage/fallout_storage.py
from UnitBase import INV_ID_CLEAR_VEHICLE
from account_helpers import AccountSettings
from account_helpers.AccountSettings import FALLOUT_VEHICLES
from account_helpers.settings_core import g_settingsCore
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from constants import FALLOUT_BATTLE_TYPE
from gui.prb_control.storage.local_storage import LocalStorage
from gui.server_events import g_eventsCache
from gui.shared import g_itemsCache
_SETTINGS_DEFAULTS = {'isEnabled': False,
 'isAutomatch': False,
 'falloutBattleType': FALLOUT_BATTLE_TYPE.UNDEFINED,
 'hasVehicleLvl8': False,
 'hasVehicleLvl10': False}

class FalloutLocalStorage(LocalStorage):
    __slots__ = ('__settings', '__intCDs')

    def __init__(self):
        super(FalloutLocalStorage, self).__init__()
        self.__settings = {}
        self.__intCDs = {}

    def init(self):
        pass

    def fini(self):
        self.__settings.clear()
        self.__intCDs.clear()

    def swap(self):
        self.__settings = g_settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.FALLOUT, _SETTINGS_DEFAULTS)
        self.__intCDs = AccountSettings.getFavorites(FALLOUT_VEHICLES)
        self.validateSelectedVehicles()

    def release(self):
        self.__settings['isEnabled'] = True
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)

    def suspend(self):
        self.__settings['isEnabled'] = False
        self.__settings['falloutBattleType'] = FALLOUT_BATTLE_TYPE.UNDEFINED
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)

    def isEnabled(self):
        return g_eventsCache.isEventEnabled() and bool(self.__settings['isEnabled'])

    def getBattleType(self):
        return self.__settings['falloutBattleType']

    def setBattleType(self, value):
        raise value in FALLOUT_BATTLE_TYPE.ALL or AssertionError('Unsupported battle type {} given!'.format(value))
        self.__settings['falloutBattleType'] = value
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)

    def isAutomatch(self):
        return bool(self.__settings['isAutomatch'])

    def setAutomatch(self, isAutomatch):
        self.__settings['isAutomatch'] = isAutomatch
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)

    def getVehiclesInvIDs(self, excludeEmpty = False):
        vehiclesIntCDs = self.__intCDs[self.getBattleType()]
        vehiclesInvIDs = []
        for intCD in vehiclesIntCDs:
            vehicle = g_itemsCache.items.getItemByCD(intCD)
            if vehicle is None:
                if not excludeEmpty:
                    vehiclesInvIDs.append(INV_ID_CLEAR_VEHICLE)
            else:
                vehiclesInvIDs.append(vehicle.invID)

        return vehiclesInvIDs

    def setVehiclesInvIDs(self, vehicles):
        vehiclesIntCDs = []
        for invID in vehicles:
            vehicle = g_itemsCache.items.getVehicle(invID)
            if vehicle is None:
                vehiclesIntCDs.append(INV_ID_CLEAR_VEHICLE)
            else:
                vehiclesIntCDs.append(vehicle.intCD)

        self.__intCDs[self.getBattleType()] = vehiclesIntCDs
        AccountSettings.setFavorites(FALLOUT_VEHICLES, self.__intCDs)
        return

    def getSelectedVehicles(self):
        return filter(None, map(g_itemsCache.items.getItemByCD, self.__intCDs[self.getBattleType()]))

    def validateSelectedVehicles(self):
        maxVehs = self.getConfig().maxVehiclesPerPlayer
        valid = [INV_ID_CLEAR_VEHICLE] * maxVehs
        battleType = self.getBattleType()
        vehicles = self.__intCDs.get(battleType, ())
        vehGetter = g_itemsCache.items.getItemByCD
        for idx, intCD in enumerate(vehicles[:maxVehs]):
            invVehicle = vehGetter(intCD)
            if invVehicle is not None and invVehicle.isInInventory:
                valid[idx] = intCD

        if valid != vehicles:
            self.__intCDs[battleType] = valid
            AccountSettings.setFavorites(FALLOUT_VEHICLES, self.__intCDs)
            return True
        else:
            return False

    def getConfig(self):
        return g_eventsCache.getFalloutConfig(self.getBattleType())

    def isModeSelected(self):
        return self.isEnabled()

    def isBattleTypeSelected(self):
        return self.isEnabled() and self.getBattleType() != FALLOUT_BATTLE_TYPE.UNDEFINED

    def hasVehicleLvl8(self):
        return bool(self.__settings['hasVehicleLvl8'])

    def setHasVehicleLvl8(self):
        self.__settings['hasVehicleLvl8'] = True
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)

    def hasVehicleLvl10(self):
        return bool(self.__settings['hasVehicleLvl10'])

    def setHasVehicleLvl10(self):
        self.__settings['hasVehicleLvl10'] = True
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)

    def setHasVehicleLvls(self, hasVehicleLvl8 = False, hasVehicleLvl10 = False):
        self.__settings['hasVehicleLvl8'] = hasVehicleLvl8
        self.__settings['hasVehicleLvl10'] = hasVehicleLvl10
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)
