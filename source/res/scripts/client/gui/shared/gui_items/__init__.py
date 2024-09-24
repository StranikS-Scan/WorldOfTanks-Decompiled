# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/__init__.py
import logging
from typing import TYPE_CHECKING
from gui.impl import backport
from gui.impl.backport import getNiceNumberFormat
from gui.impl.gen import R
from gui.shared.items_parameters.param_name_helper import getVehicleParameterText
from shared_utils import CONST_CONTAINER
from items import ITEM_TYPE_NAMES, vehicles, ITEM_TYPE_INDICES, EQUIPMENT_TYPES, getTypeOfCompactDescr
from gui.shared.money import Currency
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from helpers import dependency
if TYPE_CHECKING:
    from typing import Set, FrozenSet, Union
_logger = logging.getLogger(__name__)
CLAN_LOCK = 1
GUI_ITEM_TYPE_NAMES = tuple(ITEM_TYPE_NAMES) + tuple(['reserved'] * (16 - len(ITEM_TYPE_NAMES)))
GUI_ITEM_TYPE_NAMES += ('dossierAccount', 'dossierVehicle', 'dossierTankman', 'achievement', 'tankmanSkill', 'battleBooster', 'badge', 'battleAbility', 'lootBox', 'demountKit', 'vehPostProgression', 'recertificationForm', 'paint', 'camouflage', 'modification', 'outfit', 'style', 'decal', 'emblem', 'inscription', 'projectionDecal', 'insignia', 'personalNumber', 'sequence', 'attachment')
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
    RECERTIFICATION_FORM = GUI_ITEM_TYPE_INDICES['recertificationForm']
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
    VEH_POST_PROGRESSION = GUI_ITEM_TYPE_INDICES['vehPostProgression']
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


def getItemTypeID(bonusName):
    if bonusName in GUI_ITEM_TYPE_INDICES:
        return GUI_ITEM_TYPE_INDICES[bonusName]
    else:
        itemTypeID = None
        if bonusName == 'projection_decal':
            itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL
        elif bonusName == 'personal_number':
            itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER
        return itemTypeID


def formatMoneyError(currency):
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
    NOT_ENOUGH_GOLD = formatMoneyError(Currency.GOLD)
    NOT_ENOUGH_CREDITS = formatMoneyError(Currency.CREDITS)
    NOT_ENOUGH_CRYSTAL = formatMoneyError(Currency.CRYSTAL)
    NOT_ENOUGH_EVENT_COIN = formatMoneyError(Currency.EVENT_COIN)
    NOT_ENOUGH_BPCOIN = formatMoneyError(Currency.BPCOIN)
    NOT_ENOUGH_EQUIP_COIN = formatMoneyError(Currency.EQUIP_COIN)
    NOT_ENOUGH_CURRENCIES = (NOT_ENOUGH_GOLD,
     NOT_ENOUGH_CRYSTAL,
     NOT_ENOUGH_CREDITS,
     NOT_ENOUGH_EVENT_COIN,
     NOT_ENOUGH_BPCOIN,
     NOT_ENOUGH_EQUIP_COIN)
    NOT_ENOUGH_MONEY = 'not_enough_money'

    @classmethod
    def getCurrencyError(cls, currency):
        return formatMoneyError(currency)

    @classmethod
    def isCurrencyError(cls, errCode):
        return errCode in GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CURRENCIES


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
    return tags in vTags if isinstance(tags, str) else not vTags.isdisjoint(tags)


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
    __slots__ = ('__name', '__value', '__type', '__specValue', '__vehicleTypes', '__isDebuff', '__isSituational')

    class Name(CONST_CONTAINER):
        COMPOUND_KPI = 'compoundKPI'
        VEHICLE_REPAIR_SPEED = 'vehicleRepairSpeed'
        VEHICLE_CHASSIS_REPAIR_SPEED = 'vehicleChassisRepairSpeed'
        VEHICLE_CHASSIS_REPAIR_TIME = 'vehicleChassisRepairTime'
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
        VEHICLE_GUN_SHOT_DISPERSION_AFTER_SHOT = 'vehicleGunShotDispersionAfterShot'
        VEHICLE_GUN_SHOT_DISPERSION_CHASSIS_MOVEMENT = 'vehicleGunShotDispersionChassisMovement'
        VEHICLE_GUN_SHOT_DISPERSION_CHASSIS_ROTATION = 'vehicleGunShotDispersionChassisRotation'
        VEHICLE_GUN_SHOT_DISPERSION_TURRET_ROTATION = 'vehicleGunShotDispersionTurretRotation'
        VEHICLE_GUN_SHOT_DISPERSION_WHILE_GUN_DAMAGED = 'vehicleGunShotDispersionWhileGunDamaged'
        VEHICLE_GUN_SHOT_FULL_DISPERSION = 'vehicleGunShotFullDispersion'
        VEHICLE_AMMO_BAY_STRENGTH = 'vehicleAmmoBayStrength'
        VEHICLE_FUEL_TANK_STRENGTH = 'vehicleFuelTankStrength'
        VEHICLE_ENGINE_STRENGTH = 'vehicleEngineStrength'
        VEHICLE_CHASSIS_STRENGTH = 'vehicleChassisStrength'
        VEHICLE_AMMO_BAY_ENGINE_FUEL_STRENGTH = 'vehicleAmmoBayEngineFuelStrength'
        VEHICLE_CHASSIS_LOAD = 'vehicleChassisLoad'
        VEHICLE_CHASSIS_FALL_DAMAGE = 'vehicleChassisFallDamage'
        VEHICLE_RAM_DAMAGE_RESISTANCE = 'vehicleRamDamageResistance'
        VEHICLE_DAMAGE_ENEMIES_BY_RAMMING = 'damageEnemiesByRamming'
        VEHICLE_SOFT_GROUND_PASSABILITY = 'vehicleSoftGroundPassability'
        VEHICLE_MEDIUM_GROUND_PASSABILITY = 'vehicleMediumGroundPassability'
        VEHICLE_ENEMY_SPOTTING_TIME = 'vehicleEnemySpottingTime'
        VEHICLE_OWN_SPOTTING_TIME = 'vehicleOwnSpottingTime'
        VEHICLE_INVISIBILITY_AFTER_SHOT = 'vehicleInvisibilityAfterShot'
        VEHICLE_RELOAD_TIME_AFTER_SHELL_CHANGE = 'vehicleReloadTimeAfterShellChange'
        VEHICLE_STRENGTH = 'vehicleStrength'
        VEHICLE_ALL_GROUND_ROTATION_SPEED = 'vehicleAllGroundRotationSpeed'
        VEHICLE_SPEED_GAIN = 'vehicleSpeedGain'
        VEHICLE_TURRET_OR_CUTTING_ROTATION_SPEED = 'vehicleTurretOrCuttingRotationSpeed'
        VEHICLE_FORWARD_MAX_SPEED = 'vehicleForwardMaxSpeed'
        VEHICLE_BACKWARD_MAX_SPEED = 'vehicleBackwardMaxSpeed'
        EQUIPMENT_PREPARATION_TIME = 'equipmentPreparationTime'
        DAMAGE_AND_PIERCING_DISTRIBUTION_LOWER_BOUND = 'damageAndPiercingDistributionLowerBound'
        DAMAGE_AND_PIERCING_DISTRIBUTION_UPPER_BOUND = 'damageAndPiercingDistributionUpperBound'
        PENALTY_TO_DAMAGED_SURVEYING_DEVICE = 'penaltyToDamagedSurveyingDevice'
        STUN_RESISTANCE_EFFECT_FACTOR = 'stunResistanceEffectFactor'
        ART_NOTIFICATION_DELAY_FACTOR = 'artNotificationDelayFactor'
        MEDIUM_GROUND_FACTOR = 'mediumGroundFactor'
        SOFT_GROUND_FACTOR = 'softGroundFactor'
        WHEELS_ROTATION_SPEED = 'wheelsRotationSpeed'
        VEHICLE_FUEL_TANK_LESION_CHANCE = 'vehicleFuelTankLesionChance'
        FOLIAGE_MASKING_FACTOR = 'foliageMaskingFactor'
        ENEMY_MODULES_CREW_CRIT_CHANCE = 'enemyModulesCrewCritChance'
        VEHICLE_RAM_CHASSIS_DAMAGE_RESISTANCE = 'vehicleRamChassisDamageResistance'
        DAMAGED_MODULES_DETECTION_TIME = 'damagedModulesDetectionTime'
        FIRE_EXTINGUISHING_RATE = 'fireExtinguishingRate'
        WOUNDED_CREW_EFFICIENCY = 'woundedCrewEfficiency'
        VEHICLE_HE_SHELL_DAMAGE_RESISTANCE = 'vehicleHEShellDamageResistance'
        VEHICLE_FALLING_DAMAGE_RESISTANCE = 'vehicleFallingDamageResistance'
        VEHICLE_PENALTY_FOR_DAMAGED_ENGINE = 'vehPenaltyForDamagedEngine'
        VEHICLE_PENALTY_FOR_DAMAGED_AMMORACK = 'vehPenaltyForDamagedAmmorack'
        COMMANDER_LAMP_DELAY = 'commanderLampDelay'
        SHELL_VELOCITY = 'shellVelocity'
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
        CREW_SKILL_RANCOROUS = 'crewSkillRancorous'
        CREW_SKILL_RANCOROUS_DURATION = 'crewSkillRancorousDuration'
        CREW_SKILL_PEDANT = 'crewSkillPedant'
        CREW_SKILL_SMOOTH_TURRET = 'crewSkillSmoothTurret'
        CREW_SKILL_PRACTICAL = 'crewSkillPractical'
        CREW_SKILL_STUN_RESISTANCE = 'crewSkillStunResistance'
        DEMASK_FOLIAGE_FACTOR = 'demaskFoliageFactor'
        DEMASK_MOVING_FACTOR = 'demaskMovingFactor'
        GAME_XP = 'gameXp'
        GAME_FREE_XP = 'gameFreeXp'
        GAME_CREW_XP = 'gameCrewXp'
        GAME_CREDITS = 'gameCredits'
        GAME_FL_XP = 'gameFlXp'
        GAME_FREE_XP_AND_CREW_XP = 'gameFreeXpAndCrewXp'

    class Type(CONST_CONTAINER):
        MUL = 'mul'
        ADD = 'add'
        BOOST_SKILL = 'boostSkill'
        ONE_OF = 'oneOf'
        AGGREGATE_MUL = 'aggregateMul'

    def __init__(self, kpiName, kpiValue, kpiType=Type.MUL, specValue=None, vehicleTypes=None, situational=False):
        self.__name = kpiName
        self.__value = kpiValue
        self.__type = kpiType
        self.__specValue = specValue
        self.__vehicleTypes = vehicleTypes or None
        self.__isSituational = situational
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

    @property
    def situational(self):
        return self.__isSituational

    @property
    def isDebuff(self):
        from gui.shared.items_parameters.comparator import BACKWARD_QUALITY_PARAMS
        return self.isPositive if self.name in BACKWARD_QUALITY_PARAMS else not self.isPositive

    @property
    def isPositive(self):
        cmpValue = 0 if self.type == self.Type.ADD else 1
        return self.value >= cmpValue

    def getDescriptionR(self):
        return getVehicleParameterText(paramName=self.__name, isPositive=self.isPositive)

    def getLongDescriptionR(self):
        return getVehicleParameterText(paramName=self.__name, isPositive=self.isPositive, isLong=True)


def kpiAddEnding(kpiName, text):
    res = text
    ending = R.strings.tank_setup.kpi.bonus.valueTypes.dyn(kpiName, R.strings.tank_setup.kpi.bonus.valueTypes.default)()
    if ending != R.strings.tank_setup.kpi.bonus.valueTypes.default():
        res += ' '
    res += backport.text(ending)
    return res


def kpiFormatValue(kpiName, value, addEnding=True):
    res = ('+' if value > 0 else '') + getNiceNumberFormat(value)
    return kpiAddEnding(kpiName, res) if addEnding else res


def kpiFormatNoSignValue(kpiName, value, addEnding=True):
    res = getNiceNumberFormat(value)
    return kpiAddEnding(kpiName, res) if addEnding else res


def kpiFormatValueRange(kpiName, valueRange, addEnding=True):
    minValue, maxValue = valueRange
    res = '{}-{}'.format(getNiceNumberFormat(minValue), getNiceNumberFormat(maxValue))
    return kpiAddEnding(kpiName, res) if addEnding else res


def getKpiValueString(kpi, value, addEnding=True):
    if kpi.type == KPI.Type.MUL:
        value = (value - 1.0) * 100
    elif kpi.type == KPI.Type.AGGREGATE_MUL:
        minValue, maxValue = value
        formatValue = ((minValue - 1.0) * 100, (maxValue - 1.0) * 100)
        return kpiFormatValueRange(kpi.name, formatValue, addEnding)
    return kpiFormatValue(kpi.name, value, addEnding)


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


def collectKpi(descriptor, vehicle=None):
    if vehicle is None:
        return [ (mergeAggregateKpi(kpi) if kpi.type == KPI.Type.AGGREGATE_MUL else kpi) for kpi in descriptor.kpi ]
    else:
        result = []
        for kpi in descriptor.kpi:
            if kpi.type == KPI.Type.AGGREGATE_MUL:
                for subKpi in kpi.value:
                    if not subKpi.vehicleTypes or vehicle.type in subKpi.vehicleTypes:
                        result.append(subKpi)

            if not kpi.vehicleTypes or vehicle.type in kpi.vehicleTypes:
                result.append(kpi)

        return result


VEHICLE_ATTR_TO_KPI_NAME_MAP = {'repairSpeed': KPI.Name.VEHICLE_REPAIR_SPEED,
 'repairSpeedFactor': KPI.Name.VEHICLE_REPAIR_SPEED,
 'circularVisionRadius': KPI.Name.VEHICLE_CIRCULAR_VISION_RADIUS,
 'circularVisionRadiusFactor': KPI.Name.VEHICLE_CIRCULAR_VISION_RADIUS,
 'circularVisionRadiusBaseFactor': KPI.Name.VEHICLE_CIRCULAR_VISION_RADIUS,
 'gunReloadTimeFactor': KPI.Name.VEHICLE_GUN_RELOAD_TIME,
 'gunAimingTimeFactor': KPI.Name.VEHICLE_GUN_AIM_SPEED,
 'ammoBayHealthFactor': KPI.Name.VEHICLE_AMMO_BAY_STRENGTH,
 'fuelTankHealthFactor': KPI.Name.VEHICLE_FUEL_TANK_STRENGTH,
 'engineHealthFactor': KPI.Name.VEHICLE_ENGINE_STRENGTH,
 'additiveShotDispersionFactor': KPI.Name.VEHICLE_GUN_SHOT_DISPERSION,
 'movingAimingDispersion': KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_CHASSIS_MOVEMENT,
 'shotDemaskFactor': KPI.Name.VEHICLE_INVISIBILITY_AFTER_SHOT,
 'lowDamageDispersion': KPI.Name.DAMAGE_AND_PIERCING_DISTRIBUTION_LOWER_BOUND,
 'lowPenetrationDispersion': KPI.Name.DAMAGE_AND_PIERCING_DISTRIBUTION_LOWER_BOUND}
CREW_SKILL_TO_KPI_NAME_MAP = {'repair': KPI.Name.CREW_SKILL_REPAIR,
 'fireFighting': KPI.Name.CREW_SKILL_FIRE_FIGHTING,
 'camouflage': KPI.Name.CREW_SKILL_CAMOUFLAGE,
 'brotherhood': KPI.Name.CREW_SKILL_BROTHERHOOD,
 'commander_sixthSense': KPI.Name.CREW_SKILL_SIXTH_SENSE,
 'driver_virtuoso': KPI.Name.CREW_SKILL_VIRTUOSO,
 'driver_smoothDriving': KPI.Name.CREW_SKILL_SMOOTH_DRIVING,
 'gunner_smoothTurret': KPI.Name.CREW_SKILL_SMOOTH_TURRET,
 'loader_pedant': KPI.Name.CREW_SKILL_PEDANT,
 'gunner_rancorous': KPI.Name.CREW_SKILL_RANCOROUS}
AGGREGATE_TO_SINGLE_TYPE_KPI_MAP = {KPI.Type.AGGREGATE_MUL: KPI.Type.MUL}
