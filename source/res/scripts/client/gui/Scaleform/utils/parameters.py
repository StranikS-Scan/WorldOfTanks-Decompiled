# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/utils/parameters.py
# Compiled at: 2011-11-08 21:15:10
import math, BigWorld
from adisp import async, process
from helpers.i18n import makeString
from items import getTypeInfoByName
from gui.Scaleform import FEATURES

def _getShotsPerMinute(descriptor, formatValue=True):
    """
    Count shots per minute for stecified gun descriptor
    @param descriptor: dict - gun descriptor
    @param formatValue: boolean - specify apply BigWorld.wg_getNiceNumberFormat or not
    @return: number of shots per minute
    """
    if formatValue:
        return BigWorld.wg_getNiceNumberFormat(descriptor['burst'][0] * descriptor['clip'][0] * 60.0 / (descriptor['reloadTime'] + descriptor['burst'][0] * descriptor['burst'][1] + descriptor['clip'][0] * descriptor['clip'][1]))
    return descriptor['burst'][0] * descriptor['clip'][0] * 60.0 / (descriptor['reloadTime'] + descriptor['burst'][0] * descriptor['burst'][1] + descriptor['clip'][0] * descriptor['clip'][1])


class Parameters(object):

    @staticmethod
    def get(item, vehicle, callback):
        params = {'parameters': tuple(),
         'compatible': tuple()}
        if item.itemTypeName == 'vehicleGun':
            getGunParams(item, vehicle, callback)
        if item.itemTypeName == 'vehicleTurret':
            getTurretParams(item, vehicle, callback)
        if item.itemTypeName == 'vehicleEngine':
            getEngineParams(item, vehicle, callback)
        if item.itemTypeName == 'vehicleChassis':
            getChassisParams(item, vehicle, callback)
        if item.itemTypeName == 'vehicleRadio':
            getRadioParams(item, vehicle, callback)
        if item.itemTypeName == 'shell':
            getShellParams(item, vehicle, callback)
        if item.itemTypeName == 'vehicle':
            getVehicleParams(item, vehicle, callback)
        if item.itemTypeName == 'optionalDevice':
            getOptionalDeviceParams(item, vehicle, callback)
        if item.itemTypeName == 'equipment':
            getEquipmentParams(item, vehicle, callback)


def getVehicleParams(item, vehicle, callback):
    vd = item.descriptor
    if FEATURES.TECHNICAL_INFO:
        parameters = {'parameters': [('maxHealth', vd.maxHealth),
                        ('weight', '%s/%s' % (BigWorld.wg_getNiceNumberFormat(vd.physics['weight'] / 1000), BigWorld.wg_getNiceNumberFormat(vd.miscAttrs['maxWeight'] / 1000))),
                        ('enginePower', BigWorld.wg_getIntegralFormat(round(vd.physics['enginePower'] / 735.5))),
                        ('speedLimits', BigWorld.wg_getNiceNumberFormat(round(vd.physics['speedLimits'][0] * 3.6, 2))),
                        ('chassisRotationSpeed', BigWorld.wg_getNiceNumberFormat(round(180 / math.pi * vd.chassis['rotationSpeed'], 0))),
                        ('hullArmor', '%d/%d/%d' % vd.hull['primaryArmor'])]}
        if item.hasTurrets:
            parameters['parameters'].append(('turretArmor', '%d/%d/%d' % vd.turret['primaryArmor']))
        pPower = (BigWorld.wg_getIntegralFormat(round(vd.shot['piercingPower'][0] - vd.shot['piercingPower'][0] * vd.shot['shell']['piercingPowerRandomization'])), BigWorld.wg_getIntegralFormat(round(vd.shot['piercingPower'][0] + vd.shot['piercingPower'][0] * vd.shot['shell']['piercingPowerRandomization'])))
        damage = (BigWorld.wg_getIntegralFormat(round(vd.shot['shell']['damage'][0] - vd.shot['shell']['damage'][0] * vd.shot['shell']['damageRandomization'])), BigWorld.wg_getIntegralFormat(round(vd.shot['shell']['damage'][0] + vd.shot['shell']['damage'][0] * vd.shot['shell']['damageRandomization'])))
        parameters['parameters'].extend([('damage', '%s-%s' % damage),
         ('piercingPower', '%s-%s' % pPower),
         ('reloadTime', _getShotsPerMinute(vd.gun)),
         ('turretRotationSpeed' if item.hasTurrets else 'gunRotationSpeed', BigWorld.wg_getIntegralFormat(round(180.0 / math.pi * vd.turret['rotationSpeed']))),
         ('circularVisionRadius', BigWorld.wg_getIntegralFormat(vd.turret['circularVisionRadius'])),
         ('radioDistance', BigWorld.wg_getIntegralFormat(vd.radio['distance']))])
    else:
        parameters = {'parameters': []}
    parameters['base'] = []
    shortName = getTypeInfoByName('vehicleGun')['userString'] + ' ' + item.descriptor.gun['userString']
    parameters['base'].append(shortName)
    if item.hasTurrets:
        shortName = getTypeInfoByName('vehicleTurret')['userString'] + ' ' + item.descriptor.turret['userString']
        parameters['base'].append(shortName)
    shortName = getTypeInfoByName('vehicleEngine')['userString'] + ' ' + item.descriptor.engine['userString']
    parameters['base'].append(shortName)
    shortName = getTypeInfoByName('vehicleChassis')['userString'] + ' ' + item.descriptor.chassis['userString']
    parameters['base'].append(shortName)
    shortName = getTypeInfoByName('vehicleRadio')['userString'] + ' ' + item.descriptor.radio['userString']
    parameters['base'].append(shortName)
    parameters['stats'] = []
    callback(parameters)


def getCurrentVehicleParams():
    from CurrentVehicle import g_currentVehicle
    if g_currentVehicle.isPresent() and FEATURES.TECHNICAL_INFO:
        vd = g_currentVehicle.vehicle.descriptor
        pPower = (BigWorld.wg_getIntegralFormat(round(vd.shot['piercingPower'][0] - vd.shot['piercingPower'][0] * vd.shot['shell']['piercingPowerRandomization'])), BigWorld.wg_getIntegralFormat(round(vd.shot['piercingPower'][0] + vd.shot['piercingPower'][0] * vd.shot['shell']['piercingPowerRandomization'])))
        damage = (BigWorld.wg_getIntegralFormat(round(vd.shot['shell']['damage'][0] - vd.shot['shell']['damage'][0] * vd.shot['shell']['damageRandomization'])), BigWorld.wg_getIntegralFormat(round(vd.shot['shell']['damage'][0] + vd.shot['shell']['damage'][0] * vd.shot['shell']['damageRandomization'])))
        data = list()
        data.extend(('maxHealth', BigWorld.wg_getIntegralFormat(vd.maxHealth)))
        data.extend(('weight', '%s/%s' % (BigWorld.wg_getNiceNumberFormat(vd.physics['weight'] / 1000), BigWorld.wg_getNiceNumberFormat(vd.miscAttrs['maxWeight'] / 1000))))
        data.extend(('enginePower', BigWorld.wg_getIntegralFormat(round(vd.physics['enginePower'] / 735.5))))
        data.extend(('speedLimits', BigWorld.wg_getNiceNumberFormat(round(vd.physics['speedLimits'][0] * 3.6, 2))))
        data.extend(('chassisRotationSpeed', BigWorld.wg_getNiceNumberFormat(round(180.0 / math.pi * vd.chassis['rotationSpeed']))))
        data.extend(('hullArmor', '%d/%d/%d' % vd.hull['primaryArmor']))
        if g_currentVehicle.vehicle.hasTurrets:
            data.extend(('turretArmor', '%d/%d/%d' % vd.turrets[0][0]['primaryArmor']))
        data.extend(('damage', '%s-%s' % damage))
        data.extend(('piercingPower', '%s-%s' % pPower))
        data.extend(('reloadTime', _getShotsPerMinute(vd.gun)))
        data.extend(('turretRotationSpeed' if g_currentVehicle.vehicle.hasTurrets else 'gunRotationSpeed', BigWorld.wg_getIntegralFormat(round(180.0 / math.pi * vd.turret['rotationSpeed']))))
        data.extend(('circularVisionRadius', BigWorld.wg_getIntegralFormat(vd.turret['circularVisionRadius'])))
        data.extend(('radioDistance', BigWorld.wg_getIntegralFormat(vd.radio['distance'])))
        return data
    else:
        return list()


@process
def getRadioParams(item, vehicle, callback):
    curVehicle = None
    if vehicle and vehicle.descriptor.radio['id'][1] == item.descriptor['id'][1]:
        curVehicle = vehicle.name
    vehicles = yield getComponentVehicles(item)
    params = {}
    if FEATURES.TECHNICAL_INFO:
        params['parameters'] = (('radioDistance', item.descriptor['distance']), ('weight', item.descriptor['weight']))
    else:
        params['parameters'] = ()
    params['compatible'] = (('vehicles', ', '.join([ ('<font color="#658c4c"><b>%s</b></font>' if v == curVehicle else '%s') % v for v in vehicles ])),)
    callback(params)
    return


@process
def getChassisParams(item, vehicle, callback):
    curVehicle = None
    if vehicle and vehicle.descriptor.chassis['id'][1] == item.descriptor['id'][1]:
        curVehicle = vehicle.name
    vehicles = yield getComponentVehicles(item)
    params = {}
    if FEATURES.TECHNICAL_INFO:
        params['parameters'] = (('maxLoad', item.descriptor['maxLoad'] / 1000), ('rotationSpeed', round(180.0 / math.pi * item.descriptor['rotationSpeed'], 0)), ('weight', item.descriptor['weight']))
    else:
        params['parameters'] = ()
    params['compatible'] = (('vehicles', ', '.join([ ('<font color="#658c4c"><b>%s</b></font>' if v == curVehicle else '%s') % v for v in vehicles ])),)
    callback(params)
    return


@process
def getEngineParams(item, vehicle, callback):
    curVehicle = None
    if vehicle and vehicle.descriptor.engine['id'][1] == item.descriptor['id'][1]:
        curVehicle = vehicle.name
    vehicles = yield getComponentVehicles(item)
    params = {}
    if FEATURES.TECHNICAL_INFO:
        params['parameters'] = (('enginePower', round(item.descriptor['power'] / 735.5, 0)), ('fireStartingChance', '%d%%' % round(item.descriptor['fireStartingChance'] * 100)), ('weight', item.descriptor['weight']))
    else:
        params['parameters'] = ()
    params['compatible'] = (('vehicles', ', '.join([ ('<font color="#658c4c"><b>%s</b></font>' if v == curVehicle else '%s') % v for v in vehicles ])),)
    callback(params)
    return


@process
def getTurretParams(item, vehicle, callback):
    curGun = None
    curVehicle = None
    if vehicle and vehicle.descriptor.turret['id'][1] == item.descriptor['id'][1]:
        curGun = vehicle.descriptor.gun['userString']
        curVehicle = vehicle.name
    vehicles = yield getComponentVehicles(item)
    params = {}
    if FEATURES.TECHNICAL_INFO:
        params['parameters'] = (('armor', '%d/%d/%d' % item.descriptor['primaryArmor']),
         ('rotationSpeed', BigWorld.wg_getIntegralFormat(round(180.0 / math.pi * item.descriptor['rotationSpeed']))),
         ('circularVisionRadius', round(item.descriptor['circularVisionRadius'], 0)),
         ('weight', item.descriptor['weight']))
    else:
        params['parameters'] = ()
    params['compatible'] = (('vehicles', ', '.join([ ('<font color="#658c4c"><b>%s</b></font>' if v == curVehicle else '%s') % v for v in vehicles ])), ('guns', ', '.join([ ('<font color="#658c4c"><b>%s</b></font>' if gun['userString'] == curGun else '%s') % gun['userString'] for gun in item.descriptor['guns'] ])))
    callback(params)
    return


@process
def getGunParams(item, vehicle, callback):
    from requesters import StatsRequester
    money = yield StatsRequester().getCredits()
    turrets = set()
    curTurret = None
    curVehicle = None
    vehicles = []
    descriptors = []
    if vehicle:
        if vehicle.descriptor.gun['id'][1] == item.descriptor['id'][1]:
            curTurret = vehicle.descriptor.turret['userString']
            curVehicle = vehicle.name
        for gun in vehicle.descriptor.turret['guns']:
            if gun['id'][1] == item.descriptor['id'][1]:
                descriptors.append(gun)

        if not descriptors:
            for vTurrets in vehicle.descriptor.type.turrets:
                for turret in vTurrets:
                    for gun in turret['guns']:
                        if gun['id'][1] == item.descriptor['id'][1]:
                            descriptors.append(gun)

    from requesters import Requester, _getComponentsByType, ITEM_TYPE_INDICES
    allVehicles = yield Requester('vehicle').getFromShop(nation=item.nation)
    for v in allVehicles:
        guns = _getComponentsByType(v, ITEM_TYPE_INDICES[item.itemTypeName])
        if item.compactDescr in guns.keys():
            vehicles.append(v.name)
        for vTurrets in v.descriptor.type.turrets:
            for turret in vTurrets:
                for gun in turret['guns']:
                    if gun['id'][1] == item.descriptor['id'][1]:
                        if v.type not in ('AT-SPG', 'SPG'):
                            turrets.add(turret['userString'])
                        if vehicle is None:
                            descriptors.append(gun)

    reloadTime = {}
    dispertionRadius = {}
    aimingTime = {}
    for d in descriptors:
        rT = _getShotsPerMinute(d, False)
        findMinMax(reloadTime, rT)
        findMinMax(dispertionRadius, round(d['shotDispersionAngle'] * 100, 2))
        findMinMax(aimingTime, round(d['aimingTime'], 1))

    piercingPower = []
    damage = []
    shells = []
    for shot in item.descriptor['shots']:
        piercingPower.append('%d' % shot['piercingPower'][0])
        damage.append('%d' % shot['shell']['damage'][0])
        shells.append(makeString('#item_types:shell/kinds/' + shot['shell']['kind']))

    parameters = {}
    if FEATURES.TECHNICAL_INFO:
        parameters['parameters'] = (('caliber', item.descriptor['shots'][0]['shell']['caliber']),
         ('reloadTime', getMinMaxAsString(reloadTime)),
         ('avgPiercingPower', '/'.join(piercingPower)),
         ('avgDamage', '/'.join(damage)),
         ('dispertionRadius', getMinMaxAsString(dispertionRadius)),
         ('aimingTime', getMinMaxAsString(aimingTime)),
         ('weight', item.descriptor['weight']))
    else:
        parameters['parameters'] = ()
    parameters['compatible'] = [('vehicles', ', '.join([ ('<font color="#658c4c"><b>%s</b></font>' if v == curVehicle else '%s') % v for v in vehicles ]))]
    if turrets:
        parameters['compatible'].append(('turrets', ', '.join([ ('<font color="#658c4c"><b>%s</b></font>' if t == curTurret else '%s') % t for t in turrets ])))
    parameters['compatible'].append(('shells', ', '.join(shells)))
    callback(parameters)
    return


@async
@process
def getComponentVehicles(item, callback):
    vehicles = []
    from requesters import Requester, _getComponentsByType, ITEM_TYPE_INDICES
    allVehicles = yield Requester('vehicle').getFromShop(nation=item.nation)
    for v in allVehicles:
        components = _getComponentsByType(v, ITEM_TYPE_INDICES[item.itemTypeName])
        if item.compactDescr in components.keys():
            vehicles.append(v.name)

    callback(vehicles)


@process
def getShellParams(item, vehicle, callback):
    from requesters import StatsRequester
    money = yield StatsRequester().getCredits()
    guns = []
    descriptors = []
    if vehicle:
        for turrets in vehicle.descriptor.type.turrets:
            for turret in turrets:
                for gun in turret['guns']:
                    for shot in gun['shots']:
                        if shot['shell']['id'][1] == item.descriptor['id'][1]:
                            if gun['userString'] not in guns:
                                guns.append(gun['userString'])
                            if gun == vehicle.descriptor.gun:
                                descriptors.append(shot)

    else:
        from requesters import Requester
        allGuns = yield Requester('vehicleGun').getFromShop(nation=item.nation)
        for gun in allGuns:
            for shot in gun.descriptor['shots']:
                if shot['shell']['id'][1] == item.descriptor['id'][1]:
                    if gun.descriptor['userString'] not in guns:
                        guns.append(gun.descriptor['userString'])
                        descriptors.append(shot)

    piercingPower = {}
    damage = {}
    for d in descriptors:
        findMinMax(piercingPower, round(d['piercingPower'][0] + d['piercingPower'][0] * d['shell']['piercingPowerRandomization']))
        findMinMax(piercingPower, round(d['piercingPower'][0] - d['piercingPower'][0] * d['shell']['piercingPowerRandomization']))
        findMinMax(damage, round(d['shell']['damage'][0] + d['shell']['damage'][0] * d['shell']['damageRandomization']))
        findMinMax(damage, round(d['shell']['damage'][0] - d['shell']['damage'][0] * d['shell']['damageRandomization']))

    parameters = {}
    if FEATURES.TECHNICAL_INFO:
        parameters['parameters'] = [('caliber', item.descriptor['caliber']), ('piercingPower', getMinMaxAsString(piercingPower)), ('damage', getMinMaxAsString(damage))]
        if item.type == 'HIGH_EXPLOSIVE':
            parameters['parameters'].append(('explosionRadius', '%.2f' % item.descriptor['explosionRadius']))
    else:
        parameters['parameters'] = ()
    parameters['compatible'] = (('shellGuns', ', '.join(guns)),)
    callback(parameters)


@process
def getOptionalDeviceParams(item, vehicle, callback):
    weight = 0
    from requesters import Requester
    allVehicles = yield Requester('vehicle').getFromShop()
    if vehicle:
        index = None
        if item.descriptor in vehicle.descriptor.optionalDevices:
            index = vehicle.descriptor.optionalDevices.index(item.descriptor)
            vehicle.descriptor.removeOptionalDevice(index)
        mods = item.descriptor.weightOnVehicle(vehicle.descriptor)
        weight = math.ceil(vehicle.descriptor.physics['weight'] * mods[0] + mods[1])
        if index is not None:
            vehicle.descriptor.installOptionalDevice(item.compactDescr, index)
    else:
        weight = {}
        for vehicle in allVehicles:
            if not item.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)[0]:
                continue
            mods = item.descriptor.weightOnVehicle(vehicle.descriptor)
            findMinMax(weight, math.ceil(vehicle.descriptor.physics['weight'] * mods[0] + mods[1]))

        if weight:
            weight = getMinMaxAsString(weight)
    parameters = {'parameters': [],
     'compatible': ()}
    if weight and weight != '0' and FEATURES.TECHNICAL_INFO:
        parameters['parameters'].append(('weight', weight))
    callback(parameters)
    return


def getEquipmentParams(item, vehicle, callback):
    parameters = {'parameters': [],
     'compatible': ()}
    callback(parameters)


def findMinMax(target, value):
    if not target:
        target['min'] = value
        target['max'] = value
    else:
        if target['min'] > value:
            target['min'] = value
        if target['max'] < value:
            target['max'] = value


def getMinMaxAsString(m):
    min = BigWorld.wg_getNiceNumberFormat(m['min'])
    max = BigWorld.wg_getNiceNumberFormat(m['max'])
    if m['min'] == m['max']:
        return min
    return '%s-%s' % (min, max)
