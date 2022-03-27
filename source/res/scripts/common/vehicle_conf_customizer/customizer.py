# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/vehicle_conf_customizer/customizer.py
import random
import items
import items.customizations as vc
from functools import partial
from constants import SHELL_TYPES
from items import tankmen, vehicles, parseIntCompactDescr
from items.components.c11n_constants import SeasonType, ApplyArea, CustomizationDisplayType
from post_progression_common import TankSetups, TankSetupGroupsId

class VEHICLE_PRESET_QUALITY:
    MIN_QUALITY = 0
    MID_QUALITY = 1
    MAX_QUALITY = 2


def buildCustomizedVehicle(mvc, initialVehCompDescr, arenaKind, logger):
    vehDescr = vehicles.VehicleDescr(initialVehCompDescr)
    vehiclePresetData = _makeVehiclePreset(mvc, vehDescr)
    vehDescr.chassis = _selectItemByQuality(vehDescr.type.chassis, vehiclePresetData['modules']['track'])
    vehDescr.engine = _selectItemByQuality(vehDescr.type.engines, vehiclePresetData['modules']['engine'])
    vehDescr.radio = _selectItemByQuality(vehDescr.type.radios, vehiclePresetData['modules']['radio'])
    vehDescr.turret = _selectItemByQuality(vehDescr.type.turrets[0], vehiclePresetData['modules']['turret'])
    vehGun = _setGunFromGunName(vehDescr.turret.guns, vehiclePresetData['modules']['gunName'])
    if vehGun is None:
        vehGun = _selectGunByQuality(vehDescr, vehiclePresetData['modules']['gun'])
    vehDescr.gun = vehGun
    mayInstall, reason = vehDescr.mayInstallTurret(vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
    if not mayInstall and reason == 'not for current vehicle':
        properTurret = _findTurretForGun(vehDescr.type.turrets[0], vehDescr.gun)
        if properTurret is not None:
            vehDescr.turret = properTurret
        else:
            logger.error('May not find a turret for a gun on the bot vehicle. %r, %r', vehDescr.gun, vehDescr.name)
    mayInstall, reason = vehDescr.mayInstallTurret(vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
    if not mayInstall and reason == 'too heavy':
        vehDescr.chassis = _selectItemByQuality(vehDescr.type.chassis, VEHICLE_PRESET_QUALITY.MAX_QUALITY)
    mayInstall, reason = vehDescr.mayInstallTurret(vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
    if not mayInstall:
        logger.error('May not install all modules on the bot vehicle. %r, %r', reason, vehDescr.name)
    vehDescr.installTurret(vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
    vehDescr, optionalDevices = _fillOptionalDevices(vehDescr, vehicles, vehiclePresetData)
    defaultMaxAmmo = vehDescr.gun.maxAmmo
    defaultAmmoForGun = vehicles.getDefaultAmmoForGun(vehDescr.gun)
    vehAmmo, vehSetups, vehSetupsIndexes = _fillGunWithAmmo(defaultAmmoForGun, defaultMaxAmmo, vehiclePresetData, vehicles)
    skillLevel = vehiclePresetData['skillLevel']
    totalPerks = vehiclePresetData['perks']
    vehInfo = {'vehiclePresetData': vehiclePresetData,
     'vehAmmo': vehAmmo,
     'vehCrew': _fillCrewPerks(vehDescr.type, vehiclePresetData, skillLevel, totalPerks),
     'vehCompDescr': vehDescr.makeCompactDescr(),
     'vehSetups': vehSetups,
     'vehSetupsIndexes': vehSetupsIndexes}
    if random.random() < vehiclePresetData['camo']:
        vehInfo['vehOutfit'] = _getRandomCamoOutfit(arenaKind, vehDescr.type)
    vehInfo['vehSetups'].update({TankSetups.OPTIONAL_DEVICES: [optionalDevices]})
    return vehInfo


def _makeVehiclePreset(mvc, vehDescr):
    vehType = vehDescr.type
    vehicleClass = vehicles.getVehicleClassFromVehicleType(vehType)
    tierSettings = mvc['tiers'][vehDescr.level]
    classSettings = mvc['tankClasses'][vehicleClass]
    currentVehicleSettings = mvc['vehicles'].get(vehType.compactDescr, None)
    vehiclePresetData = {}
    vehiclePresetData.update(tierSettings)
    vehiclePresetData.update(classSettings)
    if currentVehicleSettings is not None:
        vehiclePresetData.update(currentVehicleSettings)
    return vehiclePresetData


def _selectItemByQuality(items, quality):
    itemsCount = len(items)
    if itemsCount == 0:
        return None
    elif itemsCount == 1 or quality == VEHICLE_PRESET_QUALITY.MIN_QUALITY:
        return items[0]
    elif itemsCount == 2:
        return items[1]
    else:
        if quality == VEHICLE_PRESET_QUALITY.MID_QUALITY:
            if itemsCount > 3:
                return random.choice(items[1:-1])
            else:
                return items[1]
        else:
            return items[itemsCount - 1]
        return None


def _setGunFromGunName(vehicleGuns, gunName):
    for gun in vehicleGuns:
        if gun.name == gunName:
            return gun

    return None


def _selectGunByQuality(vDescr, quality):
    allGuns, guns = _prepareGunLists(vDescr)
    if not guns:
        return None
    else:
        stockGun = guns[0]
        vehicleLevel = vDescr.level
        gunsWithProperLevel = [ gun for gun in guns if gun.level >= vehicleLevel - 1 ]
        stockGunRemoved = len(gunsWithProperLevel) < len(guns)
        if not gunsWithProperLevel and allGuns:
            gunsWithProperLevel = [ gun for gun in allGuns if gun.level >= vehicleLevel - 1 ]
            stockGunRemoved = True
        if gunsWithProperLevel:
            guns = gunsWithProperLevel
            if stockGunRemoved:
                stockGun = _findWorstGun(guns)
        if len(guns) == 1 or quality == VEHICLE_PRESET_QUALITY.MIN_QUALITY:
            return stockGun
        guns.remove(stockGun)
        stockGunLvl = stockGun.level
        stockGunHE = stockGun.shots[0].shell.kind == SHELL_TYPES.HIGH_EXPLOSIVE
        validMidTopGuns = [ gun for gun in guns if gun.level >= stockGunLvl and (gun.shots[0].shell.kind != SHELL_TYPES.HIGH_EXPLOSIVE or stockGunHE) ]
        validGunsCount = len(validMidTopGuns)
        if validGunsCount == 0:
            return stockGun
        if validGunsCount == 1:
            return validMidTopGuns[0]
        midGuns, topGuns = _splitMidAndTopGuns(validMidTopGuns, vDescr)
        if not midGuns:
            return random.choice(topGuns)
        if not topGuns:
            return random.choice(midGuns)
        if quality == VEHICLE_PRESET_QUALITY.MID_QUALITY:
            return random.choice(midGuns)
        if quality == VEHICLE_PRESET_QUALITY.MAX_QUALITY:
            return random.choice(topGuns)
        return stockGun
        return None


def _prepareGunLists(vehDescr):

    def isInList(module, modulesList):
        for moduleToCompare in modulesList:
            if module.name == moduleToCompare.name:
                return True

        return False

    allGunsList = []
    if len(vehDescr.type.turrets[0]) > 1:
        for turret in vehDescr.type.turrets[0]:
            for gun in turret.guns:
                if not isInList(gun, allGunsList):
                    allGunsList.append(gun)

    thisAndLowerTurretsGunsList = []
    for turret in vehDescr.type.turrets[0]:
        for gun in turret.guns:
            if not isInList(gun, thisAndLowerTurretsGunsList):
                thisAndLowerTurretsGunsList.append(gun)

        if turret == vehDescr.turret:
            break

    return (allGunsList, thisAndLowerTurretsGunsList)


def _findWorstGun(guns):
    worstGun = guns[0]
    worstLevel = worstGun.level
    worstPiercingPower = worstGun.shots[0].piercingPower[0]
    for gun in guns[1:]:
        if gun.level < worstLevel:
            worstLevel = gun.level
            worstPiercingPower = gun.shots[0].piercingPower[0]
            worstGun = gun
        if gun.level == worstLevel:
            if gun.shots[0].piercingPower[0] < worstPiercingPower:
                worstPiercingPower = gun.shots[0].piercingPower[0]
                worstGun = gun

    return worstGun


def _splitMidAndTopGuns(validMidTopGuns, vDescr):
    topGuns = []
    midGuns = []
    maxGunLevel = 0
    for gun in validMidTopGuns:
        gunLevel = gun.level
        if not _isGunUnlocksOtherGuns(vDescr, gun):
            if gunLevel > maxGunLevel:
                maxGunLevel = gunLevel
                midGuns += topGuns
                del topGuns[:]
                topGuns.append(gun)
                continue
            elif gunLevel == maxGunLevel:
                topGuns.append(gun)
                continue
        midGuns.append(gun)

    return (midGuns, topGuns)


def _isGunUnlocksOtherGuns(vDescr, module):
    if module.unlocks:
        for unlockId in module.unlocks:
            unlock = vDescr.type.unlocksDescrs[unlockId]
            childModuleCompDescr = unlock[1]
            itemTypeID, _, moduleID = parseIntCompactDescr(childModuleCompDescr)
            if itemTypeID == items.ITEM_TYPES.vehicleGun:
                return True
            if itemTypeID == items.ITEM_TYPES.vehicle:
                continue
            _, allModulesByType = vDescr.getComponentsByType(items.ITEM_TYPE_NAMES[itemTypeID])
            for childModuleCandidate in allModulesByType:
                if childModuleCandidate.compactDescr == childModuleCompDescr:
                    result = _isGunUnlocksOtherGuns(vDescr, childModuleCandidate)
                    if result:
                        return True

    return False


def _findTurretForGun(turrets, gunInQuestion):
    for turret in turrets:
        if gunInQuestion in turret.guns:
            return turret

    return None


def _fillGunWithAmmo(defaultAmmoForGun, defaultMaxAmmo, vehiclePresetData, vehicles):

    def proportion(shellsPercent, maxShells):
        if maxShells < 0:
            maxShells = 0
        result = maxShells * shellsPercent / 100
        resultIsNotInt = maxShells * shellsPercent % 100
        if resultIsNotInt:
            result += 1
        return result

    ammoProportions = vehiclePresetData['ammo']
    he = ammoProportions['he']
    gold = ammoProportions['gold']
    basic = ammoProportions['basic']
    totalShells = defaultMaxAmmo
    ammoTypesCount = 0
    currentAmmoForGun = defaultAmmoForGun
    currentAmmoLen = len(currentAmmoForGun)
    if currentAmmoLen >= 6:
        ammoTypesCount += 1
        if he > 0:
            heShellsCount = proportion(he, defaultMaxAmmo)
            if heShellsCount > totalShells:
                heShellsCount = totalShells
            currentAmmoForGun[5] = heShellsCount
            totalShells -= heShellsCount
        else:
            currentAmmoForGun[5] = 0
    if currentAmmoLen >= 4:
        ammoTypesCount += 1
        if gold > 0:
            goldShellsCount = proportion(gold, defaultMaxAmmo)
            if goldShellsCount > totalShells:
                goldShellsCount = totalShells
            currentAmmoForGun[3] = goldShellsCount
            totalShells -= goldShellsCount
        else:
            currentAmmoForGun[3] = 0
    if currentAmmoLen >= 2:
        ammoTypesCount += 1
        if basic > 0:
            basicShellsCount = proportion(basic, defaultMaxAmmo)
            if basicShellsCount > totalShells:
                basicShellsCount = totalShells
            currentAmmoForGun[1] = basicShellsCount
        else:
            currentAmmoForGun[1] = 0
    shells = currentAmmoForGun[:]
    currentAmmoForGun.extend([0,
     0,
     0,
     0,
     0,
     0])
    consumableSlots = vehiclePresetData['consumableSlots']
    equipmentIndex = ammoTypesCount * 2
    for consumable in consumableSlots:
        equipment = vehicles.g_cache.equipments()[vehicles.g_cache.equipmentIDs().get(consumable)]
        currentAmmoForGun[equipmentIndex] = equipment.compactDescr
        currentAmmoForGun[equipmentIndex + 1] = 1
        equipmentIndex += 2

    return (currentAmmoForGun, {TankSetups.EQUIPMENT: [currentAmmoForGun[len(shells):]],
      TankSetups.SHELLS: [shells],
      TankSetups.BATTLE_BOOSTERS: [[]],
      TankSetups.OPTIONAL_DEVICES: [[]]}, {TankSetupGroupsId.EQUIPMENT_AND_SHELLS: 0,
      TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS: 0})


def _fillCrewPerks(vehType, vehiclePresetData, skillLevel, totalPerks):

    def setPerks(perkKey):
        skillsMaskDict['commander'].add(vehiclePresetData[perkKey]['commander'])
        skillsMaskDict['gunner'].add(vehiclePresetData[perkKey]['gunner'])
        skillsMaskDict['driver'].add(vehiclePresetData[perkKey]['driver'])
        skillsMaskDict['radioman'].add(vehiclePresetData[perkKey]['radioman'])
        skillsMaskDict['loader'].add(vehiclePresetData[perkKey]['loader'])

    crewRoles = vehType.crewRoles
    skillsMaskDict = {'commander': set(),
     'gunner': set(),
     'driver': set(),
     'radioman': set(),
     'loader': set()}
    for i in xrange(1, totalPerks + 1):
        setPerks('perk' + str(i))

    skillsMaskDict['commander'] = tankmen.getSkillsMask(skillsMaskDict['commander'])
    skillsMaskDict['gunner'] = tankmen.getSkillsMask(skillsMaskDict['gunner'])
    skillsMaskDict['driver'] = tankmen.getSkillsMask(skillsMaskDict['driver'])
    skillsMaskDict['radioman'] = tankmen.getSkillsMask(skillsMaskDict['radioman'])
    skillsMaskDict['loader'] = tankmen.getSkillsMask(skillsMaskDict['loader'])
    return _generateTankmenForAIBot(vehType, crewRoles, skillLevel, skillsMaskDict)


def _generateTankmenForAIBot(vehType, roles, roleLevel, skillsMaskDict):
    tankmenList = []
    nationID = vehType.id[0]
    vehicleTypeID = vehType.id[1]
    prevPassports = tankmen.PassportCache()
    for i in xrange(len(roles)):
        role = roles[i]
        pg = tankmen.passport_generator(nationID, False, partial(_ai_crewMemberPreviewProducer, vehicleTypeID=vehicleTypeID, role=role[0]), tankmen.maxAttempts(10), tankmen.distinctFrom(prevPassports), tankmen.acceptOn('roles', role[0]))
        passport = next(pg)
        prevPassports.append(passport)
        skills = tankmen.generateSkills(role, skillsMaskDict[role[0]])
        tmanCompDescr = tankmen.generateCompactDescr(passport, vehicleTypeID, role[0], roleLevel, skills)
        tankmenList.append(tmanCompDescr)

    return tankmenList if len(tankmenList) == len(roles) else []


def _ai_crewMemberPreviewProducer(nationID, isPremium=False, vehicleTypeID=None, role=None):
    vehicleName = vehicles.g_cache.vehicle(nationID, vehicleTypeID).name if vehicleTypeID else None
    nationalGroups = tankmen.getNationGroups(nationID, isPremium).values()
    groups = [ g for g in nationalGroups if vehicleName in g.tags and role in g.tags ]
    if not groups:
        groups = [ g for g in nationalGroups if vehicleName in g.tags ]
    if not groups:
        groups = [ g for g in nationalGroups if role in g.tags ]
    if not groups:
        groups = nationalGroups
    group = random.choice(groups)
    return (group, (nationID,
      isPremium,
      group.isFemales,
      random.sample(group.firstNames, 1)[0],
      random.sample(group.lastNames, 1)[0],
      random.sample(group.icons, 1)[0]))


def _fillOptionalDevices(vehDescr, vehicles, vehiclePresetData):

    def checkIsDevicesValidAndSet(idx, deviceName):
        device = devices.get(optionalDeviceIDs[deviceName])
        if device is not None and device.checkCompatibilityWithVehicle(vehDescr)[0] and device.checkCompatibilityWithComponents(vehDescr):
            for installedDevice in installedDevices:
                if not installedDevice.checkCompatibilityWithOther(device):
                    return False

            installedDevices.append(device)
            vehDescr.installOptionalDevice(device.compactDescr, idx)
            return True
        else:
            return False

    devices = vehicles.g_cache.optionalDevices()
    optionalDeviceIDs = vehicles.g_cache.optionalDeviceIDs()
    settedCount = 0
    installedDevices = []
    for equipmentItem in vehiclePresetData['equipments']:
        if settedCount >= vehiclePresetData['equipmentSlots'] or settedCount >= len(vehDescr.optionalDevices):
            break
        if checkIsDevicesValidAndSet(settedCount, equipmentItem):
            settedCount += 1

    return (vehDescr, [ device.compactDescr for device in installedDevices ])


def _getRandomCamoOutfit(arenaKind, vehType):
    camouflages = vehicles.g_cache.customization20().camouflages.iteritems()
    arenaSeason = SeasonType.fromArenaKind(arenaKind)
    candidates = [ (i, camo) for i, camo in camouflages if _isCamoFitsArena(camo, arenaSeason) ]
    camouflages = _selectRandomCamo(candidates, vehType)
    decals = _getNationalEmblems(vehType)
    outfit = vc.CustomizationOutfit(camouflages=camouflages, decals=decals)
    return outfit.makeCompDescr()


def _isCamoFitsArena(camo, season):
    if not camo.season == season:
        return False
    return False if camo.customizationDisplayType != CustomizationDisplayType.HISTORICAL else True


def _selectRandomCamo(candidates, vehType):
    if len(candidates) == 0:
        return []
    random.shuffle(candidates)
    for i, camo in candidates:
        if not camo.matchVehicleType(vehType):
            continue
        randomCamo = vc.CamouflageComponent(i, appliedTo=ApplyArea.CAMOUFLAGE_REGIONS_VALUE)
        return [randomCamo]

    return []


def _getNationalEmblems(vehType):
    nationalEmblemId = vehType.defaultPlayerEmblemID
    nationalEmblems = vc.DecalComponent(id=nationalEmblemId, appliedTo=ApplyArea.EMBLEM_REGIONS_VALUE)
    return [nationalEmblems]
