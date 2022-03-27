# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/vehicle_conf_customizer/config.py
import XmlConfigReader
DEFAULT_INT_VALUE = -1
DEFAULT_STR_VALUE = 'empty'
MAX_PERK_SLOTS = 6

def readConfig(configFile, logger, sectionName='matchmaker_vehicles_customization'):
    vehiclesCustomizationData = {}
    reader = XmlConfigReader.makeReader(configFile, sectionName, True)
    tiers = {}
    for tier in reader.getSubsections('tier'):
        level, data = _getTierData(tier)
        tiers[level] = data

    vehiclesCustomizationData['tiers'] = tiers
    tankClasses = {}
    for tankClass in reader.getSubsections('tankClass'):
        tankClassName, data = _getTankClassData(tankClass)
        tankClasses[tankClassName] = data

    vehiclesCustomizationData['tankClasses'] = tankClasses
    customVehicles = {}
    for vehicle in reader.getSubsections('vehicle'):
        intCD, data = _getVehicleData(vehicle, tiers, tankClasses, logger)
        if data:
            customVehicles[intCD] = data

    vehiclesCustomizationData['vehicles'] = customVehicles
    return vehiclesCustomizationData


def _getTierData(tier):
    tierData = {}
    level = tier.readInt('level')
    tierData['level'] = level
    tierData['skillLevel'] = tier.readInt('skillLevel')
    tierData['perks'] = tier.readInt('perks')
    tierData['equipmentSlots'] = tier.readInt('equipmentSlots')
    modulesData = {'track': tier.readInt('modules/track'),
     'turret': tier.readInt('modules/turret'),
     'engine': tier.readInt('modules/engine'),
     'radio': tier.readInt('modules/radio'),
     'gun': tier.readInt('modules/gun'),
     'gunName': None}
    tierData['modules'] = modulesData
    tierData['consumableSlots'] = tier.readString('consumableSlots').split()
    ammoData = {'basic': tier.readInt('ammo/basic'),
     'gold': tier.readInt('ammo/gold'),
     'he': tier.readInt('ammo/he')}
    tierData['camo'] = tier.readFloat('camo', 0.2)
    tierData['ammo'] = ammoData
    return (level, tierData)


def _getTankClassData(tankClass):

    def setPerks(perkKey):
        tankClassData[perkKey] = {'commander': tankClass.readString(perkKey + '/commander'),
         'gunner': tankClass.readString(perkKey + '/gunner'),
         'driver': tankClass.readString(perkKey + '/driver'),
         'radioman': tankClass.readString(perkKey + '/radioman'),
         'loader': tankClass.readString(perkKey + '/loader')}

    tankClassData = {}
    tankClassName = tankClass.readString('class')
    tankClassData['class'] = tankClassName
    tankClassData['equipments'] = tankClass.readString('equipments').split()
    for i in range(1, MAX_PERK_SLOTS + 1):
        setPerks('perk' + str(i))

    return (tankClassName, tankClassData)


def _getVehicleData(vehicle, tiers, tankClasses, logger):
    vehiclesData = {}
    intCD = vehicle.readInt('intCD')
    try:
        vehiclesData['intCD'] = intCD
        tierData = _getCustomTierData(vehicle, tiers[vehicle.readInt('vehicleLevel')])
        vehiclesData.update(tierData)
        tankClassData = _getCustomTankClassData(vehicle, tankClasses[vehicle.readString('vehicleClass')])
        vehiclesData.update(tankClassData)
        return (intCD, vehiclesData)
    except:
        logger.error('Error loading custom vehicle customization params for compactDescr: %i', intCD)
        return (intCD, None)

    return None


def _getCustomTierData(tier, defaultTierData):
    tierData = {}
    skillLevel = tier.readInt('skillLevel', DEFAULT_INT_VALUE)
    if skillLevel != DEFAULT_INT_VALUE:
        tierData['skillLevel'] = skillLevel
    else:
        tierData['skillLevel'] = defaultTierData['skillLevel']
    perks = tier.readInt('perks', DEFAULT_INT_VALUE)
    if perks != DEFAULT_INT_VALUE:
        tierData['perks'] = perks
    else:
        tierData['perks'] = defaultTierData['perks']
    equipmentSlots = tier.readInt('equipmentSlots', DEFAULT_INT_VALUE)
    if equipmentSlots != DEFAULT_INT_VALUE:
        tierData['equipmentSlots'] = equipmentSlots
    else:
        tierData['equipmentSlots'] = defaultTierData['equipmentSlots']
    track = tier.readInt('modules/track', DEFAULT_INT_VALUE)
    turret = tier.readInt('modules/turret', DEFAULT_INT_VALUE)
    engine = tier.readInt('modules/engine', DEFAULT_INT_VALUE)
    radio = tier.readInt('modules/radio', DEFAULT_INT_VALUE)
    gun = tier.readInt('modules/gun', DEFAULT_INT_VALUE)
    gunName = tier.readString('modules/gunName', DEFAULT_STR_VALUE)
    modulesData = {'track': track if track != DEFAULT_INT_VALUE else defaultTierData['modules']['track'],
     'turret': turret if turret != DEFAULT_INT_VALUE else defaultTierData['modules']['turret'],
     'engine': engine if engine != DEFAULT_INT_VALUE else defaultTierData['modules']['engine'],
     'radio': radio if radio != DEFAULT_INT_VALUE else defaultTierData['modules']['radio'],
     'gun': gun if gun != DEFAULT_INT_VALUE else defaultTierData['modules']['gun'],
     'gunName': gunName if gunName != DEFAULT_STR_VALUE else None}
    tierData['modules'] = modulesData
    consumableSlots = tier.readString('consumableSlots', DEFAULT_STR_VALUE)
    if consumableSlots != DEFAULT_STR_VALUE:
        tierData['consumableSlots'] = consumableSlots.split()
    else:
        tierData['consumableSlots'] = defaultTierData['consumableSlots']
    basic = tier.readInt('ammo/basic', DEFAULT_INT_VALUE)
    gold = tier.readInt('ammo/gold', DEFAULT_INT_VALUE)
    he = tier.readInt('ammo/he', DEFAULT_INT_VALUE)
    ammoData = {'basic': basic if basic != DEFAULT_INT_VALUE else defaultTierData['ammo']['basic'],
     'gold': gold if gold != DEFAULT_INT_VALUE else defaultTierData['ammo']['gold'],
     'he': he if he != DEFAULT_INT_VALUE else defaultTierData['ammo']['he']}
    tierData['ammo'] = ammoData
    tierData['camo'] = tier.readFloat('camo', defaultTierData['camo'])
    return tierData


def _getCustomTankClassData(tankClass, defaultTankClassData):

    def setPerks(perkKey):
        commander = tankClass.readString(perkKey + '/commander', DEFAULT_STR_VALUE)
        gunner = tankClass.readString(perkKey + '/gunner', DEFAULT_STR_VALUE)
        driver = tankClass.readString(perkKey + '/driver', DEFAULT_STR_VALUE)
        radioman = tankClass.readString(perkKey + '/radioman', DEFAULT_STR_VALUE)
        loader = tankClass.readString(perkKey + '/loader', DEFAULT_STR_VALUE)
        tankClassData[perkKey] = {'commander': commander if commander != DEFAULT_STR_VALUE else defaultTankClassData[perkKey]['commander'],
         'gunner': gunner if gunner != DEFAULT_STR_VALUE else defaultTankClassData[perkKey]['gunner'],
         'driver': driver if driver != DEFAULT_STR_VALUE else defaultTankClassData[perkKey]['driver'],
         'radioman': radioman if radioman != DEFAULT_STR_VALUE else defaultTankClassData[perkKey]['radioman'],
         'loader': loader if loader != DEFAULT_STR_VALUE else defaultTankClassData[perkKey]['loader']}

    tankClassData = {}
    equipments = tankClass.readString('equipments', DEFAULT_STR_VALUE)
    if equipments != DEFAULT_STR_VALUE:
        tankClassData['equipments'] = equipments.split()
    else:
        tankClassData['equipments'] = defaultTankClassData['equipments']
    for i in range(1, MAX_PERK_SLOTS + 1):
        setPerks('perk' + str(i))

    return tankClassData
