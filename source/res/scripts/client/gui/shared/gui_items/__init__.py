# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/__init__.py
from shared_utils import CONST_CONTAINER
from items import ITEM_TYPE_NAMES, vehicles, ITEM_TYPE_INDICES, EQUIPMENT_TYPES
from gui.shared.money import Currency
CLAN_LOCK = 1
GUI_ITEM_TYPE_NAMES = tuple(ITEM_TYPE_NAMES) + tuple(['reserved'] * (16 - len(ITEM_TYPE_NAMES)))
GUI_ITEM_TYPE_NAMES += ('dossierAccount', 'dossierVehicle', 'dossierTankman', 'achievement', 'tankmanSkill', 'battleBooster', 'badge', 'battleAbility', 'paint', 'camouflage', 'modification', 'outfit', 'style', 'decal', 'emblem', 'inscription')
GUI_ITEM_TYPE_INDICES = dict(((n, idx) for idx, n in enumerate(GUI_ITEM_TYPE_NAMES)))

class GUI_ITEM_TYPE(CONST_CONTAINER):
    VEHICLE = GUI_ITEM_TYPE_INDICES['vehicle']
    CHASSIS = GUI_ITEM_TYPE_INDICES['vehicleChassis']
    TURRET = GUI_ITEM_TYPE_INDICES['vehicleTurret']
    GUN = GUI_ITEM_TYPE_INDICES['vehicleGun']
    ENGINE = GUI_ITEM_TYPE_INDICES['vehicleEngine']
    FUEL_TANK = GUI_ITEM_TYPE_INDICES['vehicleFuelTank']
    RADIO = GUI_ITEM_TYPE_INDICES['vehicleRadio']
    TANKMAN = GUI_ITEM_TYPE_INDICES['tankman']
    OPTIONALDEVICE = GUI_ITEM_TYPE_INDICES['optionalDevice']
    SHELL = GUI_ITEM_TYPE_INDICES['shell']
    EQUIPMENT = GUI_ITEM_TYPE_INDICES['equipment']
    BATTLE_ABILITY = GUI_ITEM_TYPE_INDICES['battleAbility']
    CUSTOMIZATION = GUI_ITEM_TYPE_INDICES['customizationItem']
    PAINT = GUI_ITEM_TYPE_INDICES['paint']
    CAMOUFLAGE = GUI_ITEM_TYPE_INDICES['camouflage']
    MODIFICATION = GUI_ITEM_TYPE_INDICES['modification']
    DECAL = GUI_ITEM_TYPE_INDICES['decal']
    EMBLEM = GUI_ITEM_TYPE_INDICES['emblem']
    INSCRIPTION = GUI_ITEM_TYPE_INDICES['inscription']
    OUTFIT = GUI_ITEM_TYPE_INDICES['outfit']
    STYLE = GUI_ITEM_TYPE_INDICES['style']
    COMMON = tuple(ITEM_TYPE_INDICES.keys())
    BATTLE_BOOSTER = GUI_ITEM_TYPE_INDICES['battleBooster']
    ARTEFACTS = (EQUIPMENT, OPTIONALDEVICE, BATTLE_BOOSTER)
    ACCOUNT_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierAccount']
    VEHICLE_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierVehicle']
    TANKMAN_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierTankman']
    ACHIEVEMENT = GUI_ITEM_TYPE_INDICES['achievement']
    SKILL = GUI_ITEM_TYPE_INDICES['tankmanSkill']
    BADGE = GUI_ITEM_TYPE_INDICES['badge']
    GUI = (ACCOUNT_DOSSIER,
     VEHICLE_DOSSIER,
     TANKMAN_DOSSIER,
     ACHIEVEMENT,
     SKILL,
     BADGE)
    VEHICLE_MODULES = (GUN,
     TURRET,
     ENGINE,
     CHASSIS,
     RADIO)
    VEHICLE_COMPONENTS = VEHICLE_MODULES + ARTEFACTS + (SHELL,)
    CUSTOMIZATIONS = (PAINT,
     CAMOUFLAGE,
     MODIFICATION,
     EMBLEM,
     INSCRIPTION,
     STYLE)


def _formatMoneyError(currency):
    return '{}_error'.format(currency)


class GUI_ITEM_ECONOMY_CODE(CONST_CONTAINER):
    UNDEFINED = ''
    CENTER_UNAVAILABLE = 'center_unavailable'
    UNLOCK_ERROR = 'unlock_error'
    ITEM_IS_HIDDEN = 'isHidden'
    ITEM_NO_PRICE = 'noPrice'
    ITEM_IS_DUPLICATED = 'duplicatedItem'
    WALLET_NOT_AVAILABLE = 'wallet_not_available'
    RESTORE_DISABLED = 'restore_disabled'
    NO_RENT_PRICE = 'no_rent_price'
    RENTAL_TIME_EXCEEDED = 'rental_time_exceeded'
    RENTAL_DISABLED = 'rental_disabled'
    NOT_ENOUGH_GOLD = _formatMoneyError(Currency.GOLD)
    NOT_ENOUGH_CREDITS = _formatMoneyError(Currency.CREDITS)
    NOT_ENOUGH_CRYSTAL = _formatMoneyError(Currency.CRYSTAL)
    _NOT_ENOUGH_MONEY = (NOT_ENOUGH_GOLD, NOT_ENOUGH_CRYSTAL, NOT_ENOUGH_CREDITS)

    @classmethod
    def getMoneyError(cls, currency):
        return _formatMoneyError(currency)

    @classmethod
    def isMoneyError(cls, errCode):
        return errCode in GUI_ITEM_ECONOMY_CODE._NOT_ENOUGH_MONEY


class ItemsCollection(dict):

    def filter(self, criteria):
        result = self.__class__()
        for intCD, item in self.iteritems():
            if criteria(item):
                result.update({intCD: item})

        return result

    def __repr__(self):
        return '%s<size:%d>' % (self.__class__.__name__, len(self.items()))


def getVehicleComponentsByType(vehicle, itemTypeIdx):

    def packModules(modules):
        if not isinstance(modules, list):
            modules = [modules]
        return ItemsCollection([ (module.intCD, module) for module in modules if module is not None ])

    if itemTypeIdx == vehicles._CHASSIS:
        return packModules(vehicle.chassis)
    if itemTypeIdx == vehicles._TURRET:
        return packModules(vehicle.turret)
    if itemTypeIdx == vehicles._GUN:
        return packModules(vehicle.gun)
    if itemTypeIdx == vehicles._ENGINE:
        return packModules(vehicle.engine)
    if itemTypeIdx == vehicles._FUEL_TANK:
        return packModules(vehicle.fuelTank)
    if itemTypeIdx == vehicles._RADIO:
        return packModules(vehicle.radio)
    if itemTypeIdx == vehicles._TANKMAN:
        from gui.shared.gui_items.Tankman import TankmenCollection
        return TankmenCollection([ (t.invID, t) for _, t in vehicle.crew ])
    if itemTypeIdx == vehicles._OPTIONALDEVICE:
        return packModules(vehicle.optDevices)
    if itemTypeIdx == vehicles._SHELL:
        return packModules(vehicle.shells)
    if itemTypeIdx == vehicles._EQUIPMENT:
        return ItemsCollection([ (eq.intCD, eq) for eq in vehicle.equipment.regularConsumables.getInstalledItems() ])
    return ItemsCollection()


def getVehicleSuitablesByType(vehDescr, itemTypeId, turretPID=0):
    descriptorsList = list()
    current = list()
    if itemTypeId == vehicles._CHASSIS:
        current = [vehDescr.chassis.compactDescr]
        descriptorsList = vehDescr.type.chassis
    elif itemTypeId == vehicles._ENGINE:
        current = [vehDescr.engine.compactDescr]
        descriptorsList = vehDescr.type.engines
    elif itemTypeId == vehicles._RADIO:
        current = [vehDescr.radio.compactDescr]
        descriptorsList = vehDescr.type.radios
    elif itemTypeId == vehicles._FUEL_TANK:
        current = [vehDescr.fuelTank.compactDescr]
        descriptorsList = vehDescr.type.fuelTanks
    elif itemTypeId == vehicles._TURRET:
        current = [vehDescr.turret.compactDescr]
        descriptorsList = vehDescr.type.turrets[turretPID]
    elif itemTypeId == vehicles._OPTIONALDEVICE:
        devs = vehicles.g_cache.optionalDevices()
        current = vehDescr.optionalDevices
        descriptorsList = [ dev for dev in devs.itervalues() if dev.checkCompatibilityWithVehicle(vehDescr)[0] ]
    elif itemTypeId == vehicles._EQUIPMENT:
        eqs = vehicles.g_cache.equipments()
        current = list()
        descriptorsList = [ eq for eq in eqs.itervalues() if eq.checkCompatibilityWithVehicle(vehDescr)[0] ]
    elif itemTypeId == GUI_ITEM_TYPE.BATTLE_BOOSTER:
        eqs = vehicles.g_cache.equipments()
        current = list()
        descriptorsList = [ eq for eq in eqs.itervalues() if eq.equipmentType == EQUIPMENT_TYPES.battleBoosters and eq.checkCompatibilityWithVehicle(vehDescr)[0] ]
    elif itemTypeId == GUI_ITEM_TYPE.BATTLE_ABILITY:
        eqs = vehicles.g_cache.equipments()
        current = list()
        descriptorsList = [ eq for eq in eqs.itervalues() if eq.equipmentType == EQUIPMENT_TYPES.battleAbilities and eq.checkCompatibilityWithVehicle(vehDescr) ]
    elif itemTypeId == vehicles._GUN:
        current = [vehDescr.gun.compactDescr]
        for gun in vehDescr.turret.guns:
            descriptorsList.append(gun)

        for turret in vehDescr.type.turrets[turretPID]:
            if turret is not vehDescr.turret:
                for gun in turret.guns:
                    descriptorsList.append(gun)

    elif itemTypeId == vehicles._SHELL:
        for shot in vehDescr.gun.shots:
            current.append(shot.shell.compactDescr)

        for gun in vehDescr.turret.guns:
            for shot in gun.shots:
                descriptorsList.append(shot.shell)

        for turret in vehDescr.type.turrets[turretPID]:
            if turret is not vehDescr.turret:
                for gun in turret.guns:
                    for shot in gun.shots:
                        descriptorsList.append(shot.shell)

    return (descriptorsList, current)


def getItemIconName(itemName):
    return '%s.png' % itemName.replace(':', '-')


class ACTION_ENTITY_ITEM(object):
    ACTION_NAME_IDX = 0
    ACTION_STEP_IDX = 1
    AFFECTED_ACTIONS_IDX = 2
    ENTITIES_SECTION_NAME = 'actionEntities'
    ACTIONS_SECTION_NAME = 'actions'
    STEPS_SECTION_NAME = 'steps'
