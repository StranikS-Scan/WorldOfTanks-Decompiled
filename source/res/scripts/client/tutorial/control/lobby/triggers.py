# Embedded file name: scripts/client/tutorial/control/lobby/triggers.py
import BigWorld
import dossiers2
from account_helpers.Inventory import _VEHICLE, _TANKMAN
from AccountCommands import RES_SUCCESS
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from items import vehicles, ITEM_TYPE_NAMES, tankmen
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.requesters import ShopDataParser
from tutorial.control.triggers import _Trigger, _TriggerWithValidateVar
from tutorial.logger import LOG_ERROR
__all__ = ['BonusTrigger',
 'BattleCountRequester',
 'ItemUnlockedTrigger',
 'ItemInstalledTrigger',
 'VehicleSettingTrigger',
 'EliteVehicleTrigger',
 'AccountCreditsTrigger',
 'ItemPriceTrigger',
 'ItemExperienceTrigger',
 'EquipmentInstalledTrigger',
 'InventoryItemTrigger',
 'CurVehicleCrewTrigger',
 'CurVehicleLockedTrigger',
 'CurrentVehicleTriggerTankmanLevelTrigger',
 'TankmanSkillTrigger',
 'FreeVehicleSlotTrigger']

class BonusTrigger(_Trigger):

    def __init__(self, triggerID, bonusID):
        super(BonusTrigger, self).__init__(triggerID)
        self.bonusID = bonusID

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            g_clientUpdateManager.addCallbacks({'stats.tutorialsCompleted': self.onTutorialCompleted})
        self.toggle(isOn=self.isOn(self._bonuses.getCompleted()))

    def isOn(self, tutorialsCompleted):
        result = False
        if self.bonusID > -1:
            result = tutorialsCompleted & 1 << self.bonusID != 0
        return result

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def onTutorialCompleted(self, completed):
        if completed is not None:
            self.toggle(isOn=self.isOn(completed))
        return


class BattleCountRequester(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(BattleCountRequester, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        self._gui.showWaiting('request-battle-count')
        BigWorld.player().stats.get('dossier', self.__cb_onGetDossier)

    def isOn(self, battlesCount):
        return battlesCount >= self.getVar()

    def __cb_onGetDossier(self, resultID, dossierCompDescr):
        self._gui.hideWaiting('request-battle-count')
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error on request dossier', resultID, dossierCompDescr)
            self.isRunning = False
            return
        dossierDescr = dossiers2.getAccountDossierDescr(dossierCompDescr)
        self.toggle(isOn=self.isOn(dossierDescr['a15x15']['battlesCount']))


class ItemUnlockedTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID, validateUpdateOnly = False):
        super(ItemUnlockedTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)
        self._validateUpdateOnly = validateUpdateOnly

    def run(self):
        if not self.isSubscribed:
            self.isSubscribed = True
            g_clientUpdateManager.addCallbacks({'stats.unlocks': self.onUnlocksUpdate})
        if self._validateUpdateOnly:
            return
        self.isRunning = True
        self._gui.showWaiting('request-unlocks')
        BigWorld.player().stats.get('unlocks', self.__cb_onGetUnlocks)

    def isOn(self, unlocks):
        var = self.getIterVar()
        result = var & unlocks
        isOn = len(result) > 0
        if isOn:
            self.setVar(result.pop())
        return isOn

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def __cb_onGetUnlocks(self, resultID, unlocks):
        self._gui.hideWaiting('request-unlocks')
        if resultID < 0:
            LOG_ERROR('Server return error unlocks request:', resultID)
            self.isRunning = False
            return
        self.toggle(isOn=self.isOn(unlocks))

    def onUnlocksUpdate(self, unlocks):
        if unlocks is not None:
            self.toggle(isOn=self.isOn(unlocks))
        return


class ItemInstalledTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(ItemInstalledTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'inventory.1.compDescr': self.onVehiclesUpdate})
            self.isSubscribed = True
        descriptor = g_currentVehicle.item.descriptor if g_currentVehicle.isPresent() else None
        self.toggle(isOn=self.isOn(descriptor))
        return

    def isOn(self, vehDescr):
        if vehDescr is None:
            return False
        else:
            _, installed, _ = vehDescr.getDevices()
            itemCompactDescr = self.getVar()
            return itemCompactDescr in installed

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def onVehiclesUpdate(self, vehiclesDescr):
        if vehiclesDescr is not None and g_currentVehicle.isPresent():
            vCompDescr = vehiclesDescr.get(g_currentVehicle.invID)
            if vCompDescr is not None:
                self.toggle(isOn=self.isOn(vehicles.VehicleDescr(compactDescr=vCompDescr)))
        return


class VehicleSettingTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(VehicleSettingTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'inventory.1.settings': self.onVehiclesSettingsUpdate})
            g_currentVehicle.onChanged += self.__cv_onChanged
            self.isSubscribed = True
        if not g_currentVehicle.isPresent():
            self.toggle(isOn=False)
            return
        self._gui.showWaiting('request-vehicle-settings')
        BigWorld.player().inventory.getItems(_VEHICLE, self.__cb_onGetVehicles)

    def isOn(self, settings):
        return settings & self.getVar() != 0

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__cv_onChanged
        self.isSubscribed = False
        self.isRunning = False

    def __cb_onGetVehicles(self, resultID, data):
        self._gui.hideWaiting('request-vehicle-settings')
        if resultID < 0:
            LOG_ERROR('Server return error to request inventory vehicles:', resultID)
            self.isRunning = False
            return
        vSettings = data.get('settings', {}).get(g_currentVehicle.invID, 0)
        self.toggle(isOn=self.isOn(vSettings))

    def onVehiclesSettingsUpdate(self, vSettings):
        if vSettings is not None and g_currentVehicle.isPresent():
            curVehSet = vSettings.get(g_currentVehicle.invID)
            if curVehSet is not None:
                self.toggle(isOn=self.isOn(curVehSet))
        return

    def __cv_onChanged(self):
        self.run()


class EliteVehicleTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(EliteVehicleTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            guiRoot = self._gui.getGuiRoot()
            if guiRoot is not None and hasattr(guiRoot, 'onVehicleBecomeElite'):
                g_playerEvents.onVehicleBecomeElite -= guiRoot.onVehicleBecomeElite
            g_playerEvents.onVehicleBecomeElite += self.__pe_onVehicleBecomeElite
            self.isSubscribed = True
        self._gui.showWaiting('request-elite-vehicles')
        BigWorld.player().stats.get('eliteVehicles', self.__cb_onGetEliteVehicles)
        return

    def isOn(self, eliteVehicles):
        return self.getVar() in eliteVehicles

    def clear(self):
        guiRoot = self._gui.getGuiRoot()
        if guiRoot is not None and hasattr(guiRoot, 'onVehicleBecomeElite'):
            g_playerEvents.onVehicleBecomeElite += guiRoot.onVehicleBecomeElite
        g_playerEvents.onVehicleBecomeElite -= self.__pe_onVehicleBecomeElite
        self.isSubscribed = False
        self.isRunning = False
        return

    def __cb_onGetEliteVehicles(self, resultID, eliteVehicles):
        self._gui.hideWaiting('request-elite-vehicles')
        if resultID < 0:
            LOG_ERROR('Server return error eliteVehicles request:', resultID)
            self.isRunning = False
            return
        self.toggle(isOn=self.isOn(eliteVehicles))

    def __pe_onVehicleBecomeElite(self, vehTypeCompDescr):
        isOn = self.isOn(set([vehTypeCompDescr]))
        if isOn:
            self.toggle()
        else:
            guiRoot = self._gui.getGuiRoot()
            if guiRoot is not None and hasattr(guiRoot, 'onVehicleBecomeElite'):
                guiRoot.onVehicleBecomeElite(vehTypeCompDescr)
        return


class AccountCreditsTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(AccountCreditsTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'stats.credits': self.onCreditsChanged})
            self.isSubscribed = True
        self._gui.showWaiting('request-credits')
        BigWorld.player().stats.get('credits', self.__cb_onCreditsReceived)

    def isOn(self, credits):
        return self.getVar() <= credits

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def __cb_onCreditsReceived(self, resultID, credits):
        self._gui.hideWaiting('request-credits')
        if resultID < 0:
            LOG_ERROR('Server return error credits request: ', resultID)
            self.isRunning = False
            return
        self.toggle(isOn=self.isOn(credits))

    def onCreditsChanged(self, credits):
        if credits is not None:
            self.toggle(isOn=self.isOn(credits))
        return


class ItemPriceTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(ItemPriceTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)
        self._accCredits = 0
        self._itemPrice = None
        return

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'stats.credits': self.onCreditsChanged})
            g_playerEvents.onShopResync += self.__pe_onShopResync
            self.isSubscribed = True
        self._gui.showWaiting('request-credits')
        BigWorld.player().stats.get('credits', self.__cb_onCreditsReceived)

    def isOn(self):
        return self._itemPrice is not None and self._itemPrice[0] <= self._accCredits

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onShopResync -= self.__pe_onShopResync
        self._accCredits = 0
        self._itemPrice = None
        self.isSubscribed = False
        self.isRunning = False
        return

    def __cb_onCreditsReceived(self, resultID, credits):
        self._gui.hideWaiting('request-credits')
        if resultID < 0:
            LOG_ERROR('Server return error credits request: ', resultID)
            self.isRunning = False
            return
        self._accCredits = credits
        self._gui.showWaiting('request-shop')
        itemTypeID, nationID, _ = vehicles.parseIntCompactDescr(self.getVar())
        BigWorld.player().shop.getAllItems(self.__cb_onShopItemsReceived)

    def __cb_onShopItemsReceived(self, resultID, data, _):
        self._gui.hideWaiting('request-shop')
        if resultID < 0:
            LOG_ERROR('Server return error shop %s items request:', resultID, data)
            data = ({}, set([]))
        self._itemPrice = ShopDataParser(data).getPrice(self.getVar())
        self.toggle(isOn=self.isOn())

    def onCreditsChanged(self, credits):
        if credits is not None:
            self._accCredits = credits
            self.toggle(isOn=self.isOn())
        return

    def __pe_onShopResync(self):
        self.run()


class ItemExperienceTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None, vehicleVarID = None):
        super(ItemExperienceTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)
        self._vehicleVarID = vehicleVarID
        self._vehTypeXPs = {}
        self._freeXP = 0

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'stats': self.onXpChanged})
            self.isSubscribed = True
        self._gui.showWaiting('request-xp')
        BigWorld.player().stats.get('vehTypeXP', self.__cb_onGetVehTypeXP)

    def isOn(self):
        itemCompDescr = self.getVar()
        vehCompDescr = self.vars().get(self._vehicleVarID)
        itemTypeID, nationID, compTypeID = vehicles.parseIntCompactDescr(vehCompDescr)
        if not itemTypeID == _VEHICLE:
            raise AssertionError
            vehType = vehicles.g_cache.vehicle(nationID, compTypeID)
            unlocksDescrs = vehType.unlocksDescrs
            filtered = filter(lambda info: info[1] == itemCompDescr, unlocksDescrs)
            vehTypeXP = self._vehTypeXPs.get(vehCompDescr, 0)
            result = False
            result = len(filtered) and vehTypeXP + self._freeXP >= filtered[0][0]
        return result

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False
        self._vehTypeXP = 0
        self._freeXP = 0

    def __cb_onGetVehTypeXP(self, resultID, data):
        if resultID < 0:
            LOG_ERROR('Server return error vehTypeXP request: ', resultID)
            self.isRunning = False
            self._gui.hideWaiting('request-xp')
            return
        self._vehTypeXPs = data
        BigWorld.player().stats.get('freeXP', self.__cb_onGetFreeXP)

    def __cb_onGetFreeXP(self, resultID, data):
        self._gui.hideWaiting('request-xp')
        if resultID < 0:
            LOG_ERROR('Server return error vehTypeXP request: ', resultID)
            self.isRunning = False
            return
        self._freeXP = data
        self.toggle(isOn=self.isOn())

    def onXpChanged(self, stats):
        if 'vehTypeXP' in stats or 'freeXP' in stats:
            vehTypeXPs = stats.get('vehTypeXP')
            freeXP = stats.get('freeXP')
            updated = False
            if vehTypeXPs is not None:
                self._vehTypeXPs = vehTypeXPs
                updated = True
            if freeXP is not None:
                self._freeXP = freeXP
                updated = True
            if updated:
                self.toggle(isOn=self.isOn())
        return


class EquipmentInstalledTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(EquipmentInstalledTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'inventory.1.eqs': self.onEquipmentsChanged})
            g_currentVehicle.onChanged += self.__cv_onChanged
            self.isSubscribed = True
        if not g_currentVehicle.isPresent():
            self.toggle(isOn=False)
            return
        self._gui.showWaiting('request-vehicle-equipments')
        BigWorld.player().inventory.getItems(_VEHICLE, self.__cb_onGetVehicles)

    def isOn(self, eqs):
        return self.getVar() in eqs

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__cv_onChanged
        self.isSubscribed = False
        self.isRunning = False

    def __cb_onGetVehicles(self, resultID, data):
        self._gui.hideWaiting('request-vehicle-equipments')
        if resultID < 0:
            LOG_ERROR('Server return error to request inventory vehicles:', resultID)
            self.isRunning = False
            return
        eqs = data.get('eqs', {}).get(g_currentVehicle.invID, 0)
        self.toggle(isOn=self.isOn(eqs))

    def onEquipmentsChanged(self, eqs):
        if eqs is not None and g_currentVehicle.isPresent():
            e = eqs.get(g_currentVehicle.invID)
            if e is not None:
                self.toggle(isOn=self.isOn(e))
        return

    def __cv_onChanged(self):
        self.run()


class InventoryItemTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None, itemTypeID = _VEHICLE):
        super(InventoryItemTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)
        self._itemTypeID = itemTypeID
        self._itemTypeName = ITEM_TYPE_NAMES[self._itemTypeID]

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryChanged})
            self.isSubscribed = True
        self._gui.showWaiting('request-inventory-items')
        BigWorld.player().inventory.getItems(self._itemTypeID, self.__cb_onGetItemsFromInventory)

    def isOn(self, items):
        return len(self.getIterVar() & set(items)) > 0

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def __makeIntVehCompactDescr(self, vCompDescr):
        nationID, compTypeID = vehicles.parseVehicleCompactDescr(vCompDescr)
        return vehicles.makeIntCompactDescrByID(self._itemTypeName, nationID, compTypeID)

    def __cb_onGetItemsFromInventory(self, resultID, data):
        self._gui.hideWaiting('request-inventory-items')
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error inventory {0:d} items request, responseCode = {1:d}'.format(self._itemTypeID, resultID))
            self.isRunning = False
            return
        if self._itemTypeID == _VEHICLE:
            items = map(self.__makeIntVehCompactDescr, data.get('compDescr', {}).itervalues())
        else:
            items = dict(filter(lambda item: item[1] > 0, data.iteritems()))
            items = items.keys()
        self.toggle(isOn=self.isOn(items))

    def onInventoryChanged(self, inventory):
        invItems = inventory.get(self._itemTypeID)
        if invItems is not None:
            if self._itemTypeID == _VEHICLE:
                if not self.isRunning:
                    self.run()
            else:
                var = self.getIterVar()
                removeItems = dict(filter(lambda item: item[1] is None and item[0] in var, invItems.iteritems()))
                addItems = dict(filter(lambda item: item[1] > 0 and item[0] in var, invItems.iteritems()))
                if len(addItems) or len(removeItems):
                    self.toggle(isOn=len(addItems))
        return


class _CurVehiclePropTrigger(_Trigger):

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_currentVehicle.onChanged += self.__cv_onChanged
            self.isSubscribed = True
        self.toggle(isOn=self.isOn())

    def clear(self):
        self.isRunning = False
        g_currentVehicle.onChanged -= self.__cv_onChanged
        self.isSubscribed = False

    def __cv_onChanged(self):
        self.run()


class CurVehicleCrewTrigger(_CurVehiclePropTrigger):

    def isOn(self):
        return g_currentVehicle.isCrewFull()


class CurVehicleLockedTrigger(_CurVehiclePropTrigger):

    def isOn(self):
        isOn = False
        if g_currentVehicle.isPresent():
            isOn = g_currentVehicle.isLocked()
        return isOn


class CurrentVehicleTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None, isLockedFlagID = None, isCrewFullFlagID = None):
        super(CurrentVehicleTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)
        self.__isLockedFlagID = isLockedFlagID
        self.__isCrewFullFlagID = isCrewFullFlagID

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_currentVehicle.onChanged += self.__cv_onChanged
            self.isSubscribed = True
        self.__checkCurrent()

    def isOn(self):
        result = vehIntCompDescr in self.getIterVar()
        self.setVar(g_currentVehicle.item.intCD if result else None)
        return result

    def clear(self):
        g_currentVehicle.onChanged -= self.__cv_onChanged
        self.isSubscribed = False
        self.isRunning = False

    def __checkCurrent(self):
        isOn = False
        isLocked = False
        isCrewFull = False
        if g_currentVehicle.isPresent():
            isOn = self.isOn()
            isLocked = g_currentVehicle.isLocked()
            isCrewFull = g_currentVehicle.isCrewFull()
        self._setFlagValue(self.__isLockedFlagID, isLocked)
        self._setFlagValue(self.__isCrewFullFlagID, isCrewFull)
        self.toggle(isOn=isOn)

    def __cv_onChanged(self):
        self.__checkCurrent()


class TankmanLevelTrigger(_Trigger):

    def __init__(self, triggerID, role, roleLevel, setVarID, inVehicleFlagID, specVehicleFlagID):
        super(TankmanLevelTrigger, self).__init__(triggerID)
        self._role = role
        self._roleLevel = roleLevel
        self._setVarID = setVarID
        self._inVehicleFlagID = inVehicleFlagID
        self._specVehicleFlagID = specVehicleFlagID

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'inventory.8': self.onTankmanChanged})
            g_currentVehicle.onChanged += self.__cv_onChanged
            self.isSubscribed = True
        if not g_currentVehicle.isPresent():
            self.toggle(isOn=False)
            return
        self._gui.showWaiting('request-tankman')
        BigWorld.player().inventory.getItems(_TANKMAN, self.__cb_onGetItemsFromInventory)

    def isOn(self, tankman):
        return self._role == tankman.role and self._roleLevel <= tankman.roleLevel

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__cv_onChanged
        self.isSubscribed = False
        self.isRunning = False

    def __cb_onGetItemsFromInventory(self, resultID, data):
        self._gui.hideWaiting('request-tankman')
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error inventory {0:d} items request, responseCode='.format(_TANKMAN, resultID))
            self.isRunning = False
            return
        else:
            current = g_currentVehicle.item
            compDescrs = data.get('compDescr', {})
            vehs = data.get('vehicle', {})
            descrs = map(lambda item: (item[0], tankmen.TankmanDescr(item[1])), compDescrs.iteritems())
            descrs = filter(lambda item: item[1].nationID == current.nationID and (item[1].vehicleTypeID == current.innationID or self._specVehicleFlagID is not None), descrs)
            isOn = False
            inVehicle = False
            specVehicle = False
            for idx, tankman in descrs:
                if self.isOn(tankman) and not inVehicle:
                    inVehicle = vehs.get(idx, -1) == g_currentVehicle.invID
                    if tankman.vehicleTypeID != current.innationID or not inVehicle and idx in vehs:
                        continue
                    isOn = True
                    specVehicle = True
                    if self._setVarID is not None:
                        self._tutorial.getVars().set(self._setVarID, idx)
                    if inVehicle:
                        break

            self._setFlagValue(self._inVehicleFlagID, inVehicle)
            self._setFlagValue(self._specVehicleFlagID, specVehicle)
            self.toggle(isOn=isOn)
            return

    def onTankmanChanged(self, tankmen):
        if tankmen is not None:
            self.run()
        return

    def __cv_onChanged(self):
        self.run()


class TankmanSkillTrigger(_TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(TankmanSkillTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'inventory.8': self.onTankmanChanged})
            g_currentVehicle.onChanged += self.__cv_onChanged
            self.isSubscribed = True
        if not g_currentVehicle.isPresent():
            self.toggle(isOn=False)
            return
        self._gui.showWaiting('request-tankman')
        BigWorld.player().inventory.getItems(_TANKMAN, self.__cb_onGetItemsFromInventory)

    def isOn(self, tankmanDescr):
        if tankmanDescr is None:
            return False
        else:
            tankman = tankmen.TankmanDescr(tankmanDescr)
            result = len(tankman.skills) > 0
            if result:
                self.setVar(tankman.skills[0])
            return result

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__cv_onChanged
        self.isSubscribed = True
        self.isRunning = False

    def __cb_onGetItemsFromInventory(self, resultID, data):
        self._gui.hideWaiting('request-tankman')
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error inventory {0:d} items request, responseCode='.format(_TANKMAN, resultID))
            self.isRunning = False
            return
        self.toggle(isOn=self.isOn(data.get('compDescr', {}).get(self.getVar())))

    def onTankmanChanged(self, tankmen):
        if tankmen is not None:
            self.run()
        return

    def __cv_onChanged(self):
        self.run()


class FreeVehicleSlotTrigger(_Trigger):

    def __init__(self, triggerID):
        super(FreeVehicleSlotTrigger, self).__init__(triggerID)
        self._slots = 0
        self._vehicles = 0

    def isOn(self):
        return self._slots > self._vehicles

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'': self.onClientUpdate})
            self.isSubscribed = True
        self._gui.showWaiting('request-slots')
        BigWorld.player().stats.get('slots', self.__cb_onSlotsReceived)

    def __cb_onSlotsReceived(self, resultID, slots):
        self._gui.hideWaiting('request-slots')
        if resultID < 0:
            LOG_ERROR('Server return error credits request: ', resultID)
            self.isRunning = False
            return
        self._slots = slots
        self._gui.showWaiting('request-inventory-items')
        BigWorld.player().inventory.getItems(_VEHICLE, self.__cb_onGetItemsFromInventory)

    def __cb_onGetItemsFromInventory(self, resultID, data):
        self._gui.hideWaiting('request-inventory-items')
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error inventory vehicles request, responseCode = {0:d}'.format(resultID))
            self.isRunning = False
            return
        self._vehicles = len(data.get('compDescr', {}))
        self.toggle(isOn=self.isOn())

    def onClientUpdate(self, diff):
        slots = diff.get('stats', {}).get('slots')
        if slots is not None:
            self._slots = slots
        vehDiff = diff.get('inventory', {}).get(_VEHICLE, {}).get('compDescr')
        if vehDiff is not None:
            self._gui.showWaiting('request-inventory-items')
            BigWorld.player().inventory.getItems(_VEHICLE, self.__cb_onGetItemsFromInventory)
        else:
            self.toggle(isOn=self.isOn())
        return
