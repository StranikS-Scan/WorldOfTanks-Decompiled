# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/__init__.py
import logging
from gui.impl import backport
from gui.impl.backport import getNiceNumberFormat
from gui.impl.gen import R
from shared_utils import CONST_CONTAINER
from items import ITEM_TYPE_NAMES, vehicles, ITEM_TYPE_INDICES, EQUIPMENT_TYPES, getTypeOfCompactDescr
from gui.shared.money import Currency
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from helpers import dependency
_logger = logging.getLogger(__name__)
CLAN_LOCK = 1
GUI_ITEM_TYPE_NAMES = tuple(ITEM_TYPE_NAMES) + tuple(['reserved'] * (16 - len(ITEM_TYPE_NAMES)))
GUI_ITEM_TYPE_NAMES += ('dossierAccount', 'dossierVehicle', 'dossierTankman', 'achievement', 'tankmanSkill', 'battleBooster', 'badge', 'battleAbility', 'lootBox', 'demountKit', 'paint', 'camouflage', 'modification', 'outfit', 'style', 'decal', 'emblem', 'inscription', 'projectionDecal', 'insignia', 'personalNumber', 'sequence', 'attachment')
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
    CREW_SKINS = GUI_ITEM_TYPE_INDICES['crewSkin']
    CREW_BOOKS = GUI_ITEM_TYPE_INDICES['crewBook']
    PAINT = GUI_ITEM_TYPE_INDICES['paint']
    CAMOUFLAGE = GUI_ITEM_TYPE_INDICES['camouflage']
    MODIFICATION = GUI_ITEM_TYPE_INDICES['modification']
    DECAL = GUI_ITEM_TYPE_INDICES['decal']
    EMBLEM = GUI_ITEM_TYPE_INDICES['emblem']
    INSCRIPTION = GUI_ITEM_TYPE_INDICES['inscription']
    OUTFIT = GUI_ITEM_TYPE_INDICES['outfit']
    STYLE = GUI_ITEM_TYPE_INDICES['style']
    PROJECTION_DECAL = GUI_ITEM_TYPE_INDICES['projectionDecal']
    INSIGNIA = GUI_ITEM_TYPE_INDICES['insignia']
    PERSONAL_NUMBER = GUI_ITEM_TYPE_INDICES['personalNumber']
    SEQUENCE = GUI_ITEM_TYPE_INDICES['sequence']
    ATTACHMENT = GUI_ITEM_TYPE_INDICES['attachment']
    DEMOUNT_KIT = GUI_ITEM_TYPE_INDICES['demountKit']
    COMMON = tuple(ITEM_TYPE_INDICES.keys())
    BATTLE_BOOSTER = GUI_ITEM_TYPE_INDICES['battleBooster']
    ARTEFACTS = (EQUIPMENT, OPTIONALDEVICE, BATTLE_BOOSTER)
    ACCOUNT_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierAccount']
    VEHICLE_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierVehicle']
    TANKMAN_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierTankman']
    ACHIEVEMENT = GUI_ITEM_TYPE_INDICES['achievement']
    SKILL = GUI_ITEM_TYPE_INDICES['tankmanSkill']
    BADGE = GUI_ITEM_TYPE_INDICES['badge']
    LOOT_BOX = GUI_ITEM_TYPE_INDICES['lootBox']
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
     STYLE,
     PROJECTION_DECAL,
     PERSONAL_NUMBER,
     SEQUENCE,
     ATTACHMENT)
    CUSTOMIZATIONS_WITHOUT_STYLE = (PAINT,
     CAMOUFLAGE,
     MODIFICATION,
     EMBLEM,
     INSCRIPTION,
     PROJECTION_DECAL,
     PERSONAL_NUMBER)


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
    NOT_ENOUGH_EVENT_COIN = _formatMoneyError(Currency.EVENT_COIN)
    _NOT_ENOUGH_CURRENCIES = (NOT_ENOUGH_GOLD,
     NOT_ENOUGH_CRYSTAL,
     NOT_ENOUGH_CREDITS,
     NOT_ENOUGH_EVENT_COIN)
    NOT_ENOUGH_MONEY = 'not_enough_money'

    @classmethod
    def getCurrencyError(cls, currency):
        return _formatMoneyError(currency)

    @classmethod
    def isCurrencyError(cls, errCode):
        return errCode in GUI_ITEM_ECONOMY_CODE._NOT_ENOUGH_CURRENCIES


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
        return packModules(vehicle.optDevices.installed)
    if itemTypeIdx == vehicles._SHELL:
        return packModules(vehicle.shells.installed)
    if itemTypeIdx == vehicles._EQUIPMENT:
        return ItemsCollection([ (eq.intCD, eq) for eq in vehicle.consumables.installed.getItems() ])
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


def checkForTags(vTags, tags):
    if not hasattr(tags, '__iter__'):
        tags = (tags,)
    return bool(vTags & frozenset(tags))


@dependency.replace_none_kwargs(itemsFactory=IGuiItemsFactory)
def isItemVehicleHull(intCD, vehicle, itemsFactory=None):
    typeCD = getTypeOfCompactDescr(intCD)
    if typeCD == GUI_ITEM_TYPE.CHASSIS:
        item = itemsFactory.createGuiItem(typeCD, intCompactDescr=intCD)
        hulls = vehicle.descriptor.type.hulls
        for hull in hulls:
            if item.innationID in hull.variantMatch:
                return True

    return False


class ACTION_ENTITY_ITEM(object):
    ACTION_NAME_IDX = 0
    ACTION_STEP_IDX = 1
    AFFECTED_ACTIONS_IDX = 2
    ENTITIES_SECTION_NAME = 'actionEntities'
    ACTIONS_SECTION_NAME = 'actions'
    STEPS_SECTION_NAME = 'steps'


class KPI(object):
    __slots__ = ('__name', '__value', '__type', '__specValue', '__vehicleTypes')

    class Name(CONST_CONTAINER):
        COMPOUND_KPI = 'compoundKPI'
        VEHICLE_REPAIR_SPEED = 'vehicleRepairSpeed'
        VEHICLE_CHASSIS_REPAIR_SPEED = 'vehicleChassisRepairSpeed'
        VEHICLE_ENGINE_POWER = 'vehicleEnginePower'
        VEHICLE_TURRET_ROTATION_SPEED = 'vehicleTurretRotationSpeed'
        VEHICLE_CIRCULAR_VISION_RADIUS = 'vehicleCircularVisionRadius'
        VEHICLE_STILL_CIRCULAR_VISION_RADIUS = 'vehicleStillCircularVisionRadius'
        VEHICLE_CAMOUFLAGE = 'vehicleCamouflage'
        VEHICLE_STILL_CAMOUFLAGE = 'vehicleStillCamouflage'
        VEHICLE_FIRE_CHANCE = 'vehicleFireChance'
        VEHICLE_GUN_RELOAD_TIME = 'vehicleGunReloadTime'
        VEHICLE_GUN_AIM_SPEED = 'vehicleGunAimSpeed'
        VEHICLE_GUN_SHOT_DISPERSION = 'vehicleGunShotDispersion'
        VEHICLE_GUN_SHOT_FULL_DISPERSION = 'vehicleGunShotFullDispersion'
        VEHICLE_AMMO_BAY_STRENGTH = 'vehicleAmmoBayStrength'
        VEHICLE_FUEL_TANK_STRENGTH = 'vehicleFuelTankStrength'
        VEHICLE_ENGINE_STRENGTH = 'vehicleEngineStrength'
        VEHICLE_CHASSIS_STRENGTH = 'vehicleChassisStrength'
        VEHICLE_AMMO_BAY_ENGINE_FUEL_STRENGTH = 'vehicleAmmoBayEngineFuelStrength'
        VEHICLE_CHASSIS_LOAD = 'vehicleChassisLoad'
        VEHICLE_CHASSIS_FALL_DAMAGE = 'vehicleChassisFallDamage'
        VEHICLE_RAM_OR_EXPLOSION_DAMAGE_RESISTANCE = 'vehicleRamOrExplosionDamageResistance'
        VEHICLE_SOFT_GROUND_PASSABILITY = 'vehicleSoftGroundPassability'
        VEHICLE_MEDIUM_GROUND_PASSABILITY = 'vehicleMediumGroundPassability'
        VEHICLE_ENEMY_SPOTTING_TIME = 'vehicleEnemySpottingTime'
        VEHICLE_OWN_SPOTTING_TIME = 'vehicleOwnSpottingTime'
        VEHICLE_RELOAD_TIME_AFTER_SHELL_CHANGE = 'vehicleReloadTimeAfterShellChange'
        VEHICLE_STRENGTH = 'vehicleStrength'
        VEHICLE_PENALTY_FOR_DAMAGED_ENGINE_AND_COMBAT = 'vehPenaltyForDamageEngineAndCombat'
        VEHICLE_ALL_GROUND_ROTATION_SPEED = 'vehicleAllGroundRotationSpeed'
        VEHICLE_SPEED_GAIN = 'vehicleSpeedGain'
        VEHICLE_TURRET_OR_CUTTING_ROTATION_SPEED = 'vehicleTurretOrCuttingRotationSpeed'
        VEHICLE_FORWARD_MAX_SPEED = 'vehicleForwardMaxSpeed'
        VEHICLE_BACKWARD_MAX_SPEED = 'vehicleBackwardMaxSpeed'
        VEHICLE_CAMOUFLAGE_GROUP = 'vehicleCamouflageGroup'
        VEHICLE_STILL_CAMOUFLAGE_GROUP = 'vehicleStillCamouflageGroup'
        CREW_LEVEL = 'crewLevel'
        CREW_HIT_CHANCE = 'crewHitChance'
        CREW_STUN_DURATION = 'crewStunDuration'
        CREW_REPEATED_STUN_DURATION = 'crewRepeatedStunDuration'
        CREW_SKILL_REPAIR = 'crewSkillRepair'
        CREW_SKILL_FIRE_FIGHTING = 'crewSkillFireFighting'
        CREW_SKILL_CAMOUFLAGE = 'crewSkillCamouflage'
        CREW_SKILL_BROTHERHOOD = 'crewSkillBrotherHood'
        CREW_SKILL_SIXTH_SENSE = 'crewSkillSixthSense'
        CREW_SKILL_SIXTH_SENSE_DELAY = 'crewSkillSixthSenseDelay'
        CREW_SKILL_VIRTUOSO = 'crewSkillVirtuoso'
        CREW_SKILL_SMOOTH_DRIVING = 'crewSkillSmoothRiding'
        CREW_SKILL_LAST_EFFORT = 'crewSkillLastEffort'
        CREW_SKILL_LAST_EFFORT_DURATION = 'crewSkillLastEffortDuration'
        CREW_SKILL_RANCOROUS = 'crewSkillRancorous'
        CREW_SKILL_RANCOROUS_DURATION = 'crewSkillRancorousDuration'
        CREW_SKILL_PEDANT = 'crewSkillPedant'
        CREW_SKILL_SMOOTH_TURRET = 'crewSkillSmoothTurret'
        DEMASK_FOLIAGE_FACTOR = 'demaskFoliageFactor'
        DEMASK_MOVING_FACTOR = 'demaskMovingFactor'
        GAME_XP = 'gameXp'
        GAME_FREE_XP = 'gameFreeXp'
        GAME_CREW_XP = 'gameCrewXp'
        GAME_CREDITS = 'gameCredits'
        GAME_FL_XP = 'gameFlXp'

    class Type(CONST_CONTAINER):
        MUL = 'mul'
        ADD = 'add'
        BOOST_SKILL = 'boostSkill'
        ONE_OF = 'oneOf'
        AGGREGATE_MUL = 'aggregateMul'

    def __init__(self, kpiName, kpiValue, kpyType=Type.MUL, specValue=None, vehicleTypes=None):
        self.__name = kpiName
        self.__value = kpiValue
        self.__type = kpyType
        self.__specValue = specValue
        self.__vehicleTypes = vehicleTypes or None
        return

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def specValue(self):
        return self.__specValue

    @property
    def type(self):
        return self.__type

    @property
    def vehicleTypes(self):
        return self.__vehicleTypes

    def getDescriptionR(self):
        res = R.strings.tank_setup.kpi.bonus.dyn(self.__name)
        if not res:
            _logger.debug('KPI description not found, name %s', self.__name)
            return R.invalid()
        return res()

    def getLongDescriptionR(self):
        res = R.strings.tank_setup.kpi.bonus.longDescr.dyn(self.__name)
        return res() if res else self.getDescriptionR()


def kpiFormatValue(kpiName, value):
    ending = R.strings.tank_setup.kpi.bonus.valueTypes.dyn(kpiName, R.strings.tank_setup.kpi.bonus.valueTypes.default)()
    return ('+' if value > 0 else '') + getNiceNumberFormat(value) + backport.text(ending)


def kpiFormatValueRange(kpiName, valueRange):
    ending = R.strings.tank_setup.kpi.bonus.valueTypes.dyn(kpiName, R.strings.tank_setup.kpi.bonus.valueTypes.default)()
    minValue, maxValue = valueRange
    return '{}-{}{}'.format(getNiceNumberFormat(minValue), getNiceNumberFormat(maxValue), backport.text(ending))


def getKpiValueString(kpi, value):
    if kpi.type == KPI.Type.MUL:
        value = (value - 1.0) * 100
    elif kpi.type == KPI.Type.AGGREGATE_MUL:
        minValue, maxValue = value
        formatValue = ((minValue - 1.0) * 100, (maxValue - 1.0) * 100)
        return kpiFormatValueRange(kpi.name, formatValue)
    return kpiFormatValue(kpi.name, value)


def getKpiFormatDescription(kpi):
    value = getKpiValueString(kpi, kpi.value)
    specValue = getKpiValueString(kpi, kpi.specValue) if kpi.specValue else None
    generalValue = ' / '.join((value, specValue)) if specValue is not None else value
    description = ' '.join((generalValue, backport.text(kpi.getDescriptionR(), default='')))
    return description


def mergeAggregateKpi(aggregateKpi):

    def _mergeValue(value, currentRange):
        if currentRange is None:
            return (value, value)
        else:
            minValue, maxValue = currentRange
            return (min(minValue, value), max(maxValue, value))

    if aggregateKpi.type not in (KPI.Type.AGGREGATE_MUL,):
        _logger.debug('Only aggregate kpi type supported merge')
        return aggregateKpi
    else:
        specValue = None
        vehicleTypes = []
        value = None
        for kpi in aggregateKpi.value:
            value = _mergeValue(kpi.value, value)
            if kpi.specValue:
                specValue = _mergeValue(kpi.specValue, specValue)
            if kpi.vehicleTypes:
                vehicleTypes.extend(kpi.vehicleTypes)

        return KPI(aggregateKpi.name, value, aggregateKpi.type, specValue, vehicleTypes)


VEHICLE_ATTR_TO_KPI_NAME_MAP = {'repairSpeed': KPI.Name.VEHICLE_REPAIR_SPEED,
 'repairSpeedFactor': KPI.Name.VEHICLE_REPAIR_SPEED,
 'circularVisionRadius': KPI.Name.VEHICLE_CIRCULAR_VISION_RADIUS,
 'circularVisionRadiusFactor': KPI.Name.VEHICLE_CIRCULAR_VISION_RADIUS,
 'gunReloadTimeFactor': KPI.Name.VEHICLE_GUN_RELOAD_TIME,
 'gunAimingTimeFactor': KPI.Name.VEHICLE_GUN_AIM_SPEED,
 'crewLevelIncrease': KPI.Name.CREW_LEVEL,
 'ammoBayHealthFactor': KPI.Name.VEHICLE_AMMO_BAY_STRENGTH,
 'fuelTankHealthFactor': KPI.Name.VEHICLE_FUEL_TANK_STRENGTH,
 'engineHealthFactor': KPI.Name.VEHICLE_ENGINE_STRENGTH,
 'additiveShotDispersionFactor': KPI.Name.VEHICLE_GUN_SHOT_DISPERSION}
CREW_SKILL_TO_KPI_NAME_MAP = {'repair': KPI.Name.CREW_SKILL_REPAIR,
 'fireFighting': KPI.Name.CREW_SKILL_FIRE_FIGHTING,
 'camouflage': KPI.Name.CREW_SKILL_CAMOUFLAGE,
 'brotherhood': KPI.Name.CREW_SKILL_BROTHERHOOD,
 'commander_sixthSense': KPI.Name.CREW_SKILL_SIXTH_SENSE,
 'driver_virtuoso': KPI.Name.CREW_SKILL_VIRTUOSO,
 'driver_smoothDriving': KPI.Name.CREW_SKILL_SMOOTH_DRIVING,
 'gunner_smoothTurret': KPI.Name.CREW_SKILL_SMOOTH_TURRET,
 'loader_pedant': KPI.Name.CREW_SKILL_PEDANT,
 'radioman_lastEffort': KPI.Name.CREW_SKILL_LAST_EFFORT,
 'gunner_rancorous': KPI.Name.CREW_SKILL_RANCOROUS}
AGGREGATE_TO_SINGLE_TYPE_KPI_MAP = {KPI.Type.AGGREGATE_MUL: KPI.Type.MUL}
