# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/__init__.py
import math
import sys
from math import ceil
from gui.shared.utils import SHELLS_COUNT_PROP_NAME, RELOAD_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, DISPERSION_RADIUS_PROP_NAME, AIMING_TIME_PROP_NAME, PIERCING_POWER_PROP_NAME, DAMAGE_PROP_NAME, SHELLS_PROP_NAME
from helpers import i18n, time_utils
from items import vehicles, artefacts
RELATIVE_PARAMS = ('relativePower', 'relativeArmor', 'relativeMobility', 'relativeCamouflage', 'relativeVisibility')
MAX_RELATIVE_VALUE = 1000
NO_DATA = 'no data'

def _updateMinMaxValues(targetDict, key, value):
    targetDict[key] = (min(targetDict[key][0], value), max(targetDict[key][1], value))


def getShotsPerMinute(descriptor, reloadTime):
    clip = descriptor['clip']
    burst = descriptor['burst']
    clipCount = clip[0] / (burst[0] if clip[0] > 1 else 1)
    value = burst[0] * clipCount * time_utils.ONE_MINUTE / (reloadTime + (burst[0] - 1) * burst[1] * clipCount + (clipCount - 1) * clip[1])
    return value


def calcGunParams(gunDescr, descriptors):
    result = {SHELLS_COUNT_PROP_NAME: (sys.maxint, -1),
     RELOAD_TIME_PROP_NAME: (sys.maxint, -1),
     RELOAD_MAGAZINE_TIME_PROP_NAME: (sys.maxint, -1),
     SHELL_RELOADING_TIME_PROP_NAME: (sys.maxint, -1),
     DISPERSION_RADIUS_PROP_NAME: (sys.maxint, -1),
     AIMING_TIME_PROP_NAME: (sys.maxint, -1),
     PIERCING_POWER_PROP_NAME: list(),
     DAMAGE_PROP_NAME: list(),
     SHELLS_PROP_NAME: list()}
    for descr in descriptors:
        currShellsCount = descr['clip'][0]
        if currShellsCount > 1:
            _updateMinMaxValues(result, SHELL_RELOADING_TIME_PROP_NAME, descr['clip'][1])
            _updateMinMaxValues(result, RELOAD_MAGAZINE_TIME_PROP_NAME, descr[RELOAD_TIME_PROP_NAME])
            _updateMinMaxValues(result, SHELLS_COUNT_PROP_NAME, currShellsCount)
        _updateMinMaxValues(result, RELOAD_TIME_PROP_NAME, getShotsPerMinute(descr, descr[RELOAD_TIME_PROP_NAME]))
        curDispRadius = round(descr['shotDispersionAngle'] * 100, 2)
        curAimingTime = round(descr[AIMING_TIME_PROP_NAME], 1)
        _updateMinMaxValues(result, DISPERSION_RADIUS_PROP_NAME, curDispRadius)
        _updateMinMaxValues(result, AIMING_TIME_PROP_NAME, curAimingTime)

    if 'shots' in gunDescr:
        for shot in gunDescr['shots']:
            result[PIERCING_POWER_PROP_NAME].append(shot[PIERCING_POWER_PROP_NAME][0])
            result[DAMAGE_PROP_NAME].append(shot['shell'][DAMAGE_PROP_NAME][0])
            result[SHELLS_PROP_NAME].append(i18n.makeString('#item_types:shell/kinds/' + shot['shell']['kind']))

    return result


def calcShellParams(descriptors):
    result = {PIERCING_POWER_PROP_NAME: (sys.maxint, -1),
     DAMAGE_PROP_NAME: (sys.maxint, -1)}
    for d in descriptors:
        piercingPower = d[PIERCING_POWER_PROP_NAME][0]
        shell = d['shell']
        ppRand = shell['piercingPowerRandomization']
        damageRand = shell['damageRandomization']
        curPiercingPower = (int(piercingPower - piercingPower * ppRand), int(ceil(piercingPower + piercingPower * ppRand)))
        damage = shell[DAMAGE_PROP_NAME][0]
        curDamage = (int(damage - damage * damageRand), int(ceil(damage + damage * damageRand)))
        result[PIERCING_POWER_PROP_NAME] = (min(result[PIERCING_POWER_PROP_NAME][0], curPiercingPower[0]), max(result[PIERCING_POWER_PROP_NAME][1], curPiercingPower[1]))
        result[DAMAGE_PROP_NAME] = (min(result[DAMAGE_PROP_NAME][0], curDamage[0]), max(result[DAMAGE_PROP_NAME][1], curDamage[1]))

    return result


def getEquipmentParameters(eqpDescr):
    params = dict()
    eqDescrType = type(eqpDescr)
    if eqDescrType is artefacts.Artillery:
        shellDescr = vehicles.getDictDescr(eqpDescr.shellCompactDescr)
        params.update({'damage': (shellDescr['damage'][0],) * 2,
         'piercingPower': eqpDescr.piercingPower,
         'caliber': shellDescr['caliber'],
         'shotsNumberRange': eqpDescr.shotsNumber,
         'areaRadius': eqpDescr.areaRadius,
         'artDelayRange': eqpDescr.delay})
    elif eqDescrType is artefacts.Bomber:
        shellDescr = vehicles.getDictDescr(eqpDescr.shellCompactDescr)
        params.update({'bombDamage': (shellDescr['damage'][0],) * 2,
         'piercingPower': eqpDescr.piercingPower,
         'bombsNumberRange': eqpDescr.bombsNumber,
         'areaSquare': eqpDescr.areaLength * eqpDescr.areaWidth,
         'flyDelayRange': eqpDescr.delay})
    return params


def getGunDescriptors(gunDescr, vehicleDescr):
    descriptors = []
    for gun in vehicleDescr.turret['guns']:
        if gun['id'][1] == gunDescr['id'][1]:
            descriptors.append(gun)

    if not descriptors:
        for vTurrets in vehicleDescr.type.turrets:
            for turret in vTurrets:
                for gun in turret['guns']:
                    if gun['id'][1] == gunDescr['id'][1]:
                        descriptors.append(gun)

    return descriptors


def getShellDescriptors(shellDescriptor, vehicleDescr):
    descriptors = []
    shellInNationID = shellDescriptor['id'][1]
    for shot in vehicleDescr.gun.get('shots', []):
        if shot['shell']['id'][1] == shellInNationID:
            descriptors.append(shot)

    return descriptors


def getOptionalDeviceWeight(itemDescr, vehicleDescr):
    weight = 0
    index = None
    if vehicleDescr is not None:
        if itemDescr in vehicleDescr.optionalDevices:
            index = vehicleDescr.optionalDevices.index(itemDescr)
            vehicleDescr.removeOptionalDevice(index)
        mods = itemDescr.weightOnVehicle(vehicleDescr)
        weight = math.ceil(vehicleDescr.physics['weight'] * mods[0] + mods[1])
        if index is not None:
            vehicleDescr.installOptionalDevice(itemDescr['compactDescr'], index)
    return (weight, weight)
