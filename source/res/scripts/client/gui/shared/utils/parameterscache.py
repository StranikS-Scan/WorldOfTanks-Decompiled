# Embedded file name: scripts/client/gui/shared/utils/ParametersCache.py
from gui.shared.utils import RELOAD_TIME_PROP_NAME, DISPERSION_RADIUS_PROP_NAME, AIMING_TIME_PROP_NAME, PIERCING_POWER_PROP_NAME, DAMAGE_PROP_NAME, SHELLS_PROP_NAME, SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, CLIP_VEHICLES_PROP_NAME, CLIP_VEHICLES_CD_PROP_NAME, GUN_CLIP, GUN_CAN_BE_CLIP, GUN_NORMAL
from items import artefacts
from items.vehicles import getVehicleType
import BigWorld, nations, math, sys
from debug_utils import *
from helpers import i18n
from items import vehicles

class _ParametersCache(object):
    __SEC_IN_MINUTE = 60.0

    def __init__(self):
        self.__xmlItems = {}
        self.__cache = {}
        self.__init = False
        self.__precachHandlers = {vehicles._OPTIONALDEVICE: self.__precachOptionalDevices,
         vehicles._GUN: self.__precachGuns,
         vehicles._SHELL: self.__precachShells,
         vehicles._EQUIPMENT: self.__precachEquipments}
        self.__itemTypeHandlers = {vehicles._RADIO: self.getRadioParameters,
         vehicles._ENGINE: self.getEngineParameters,
         vehicles._CHASSIS: self.getChassisParameters,
         vehicles._TURRET: self.getTurretParameters,
         vehicles._VEHICLE: self.getVehicleParameters,
         vehicles._EQUIPMENT: self.getEquipmentParameters,
         vehicles._OPTIONALDEVICE: self.getOptionalDeviceParameters,
         vehicles._GUN: self.getGunParameters,
         vehicles._SHELL: self.getShellParameters}

    @property
    def initialized(self):
        return self.__init

    def __readXMLItems(self):
        result = dict()
        for _, idx in nations.INDICES.iteritems():
            section = result.setdefault(idx, dict())
            section[vehicles._VEHICLE] = [ self.__getItemDescriptor(vehicles._VEHICLE, idx, cd) for cd in vehicles.g_list.getList(idx).keys() ]
            section[vehicles._RADIO] = [ self.__getItemDescriptor(vehicles._RADIO, idx, data['compactDescr']) for data in vehicles.g_cache.radios(idx).itervalues() ]
            section[vehicles._ENGINE] = [ self.__getItemDescriptor(vehicles._ENGINE, idx, data['compactDescr']) for data in vehicles.g_cache.engines(idx).itervalues() ]
            section[vehicles._CHASSIS] = [ self.__getItemDescriptor(vehicles._CHASSIS, idx, data['compactDescr']) for data in vehicles.g_cache.chassis(idx).itervalues() ]
            section[vehicles._TURRET] = [ self.__getItemDescriptor(vehicles._TURRET, idx, data['compactDescr']) for data in vehicles.g_cache.turrets(idx).itervalues() ]
            section[vehicles._GUN] = [ self.__getItemDescriptor(vehicles._GUN, idx, data['compactDescr']) for data in vehicles.g_cache.guns(idx).itervalues() ]
            section[vehicles._SHELL] = [ self.__getItemDescriptor(vehicles._SHELL, idx, data['compactDescr']) for data in vehicles.g_cache.shells(idx).itervalues() ]

        section = result.setdefault(nations.NONE_INDEX, dict())
        section[vehicles._EQUIPMENT] = [ self.__getItemDescriptor(vehicles._EQUIPMENT, nations.NONE_INDEX, data['compactDescr']) for data in vehicles.g_cache.equipments().itervalues() ]
        section[vehicles._OPTIONALDEVICE] = [ self.__getItemDescriptor(vehicles._OPTIONALDEVICE, nations.NONE_INDEX, data['compactDescr']) for data in vehicles.g_cache.optionalDevices().itervalues() ]
        return result

    def __getItemDescriptor(self, typeIdx, nationIdx, itemID):
        if typeIdx == vehicles._VEHICLE:
            return vehicles.VehicleDescr(typeID=(nationIdx, itemID))
        return vehicles.getDictDescr(itemID)

    def __getItems(self, typeIdx, nationIdx = None):
        if nationIdx is None:
            result = list()
            for idx in nations.INDICES.itervalues():
                vDescrs = self.__getItems(typeIdx, idx)
                if vDescrs is not None:
                    result.extend(vDescrs)

            return result
        else:
            items = self.__xmlItems.get(nationIdx, {}).get(typeIdx)
            if items is None:
                return list()
            return items

    def _getShotsPerMinute(self, descriptor):
        clipCount = descriptor['clip'][0] / (descriptor['burst'][0] if descriptor['clip'][0] > 1 else 1)
        return descriptor['burst'][0] * clipCount * 60.0 / (descriptor['reloadTime'] + (descriptor['burst'][0] - 1) * descriptor['burst'][1] + (clipCount - 1) * descriptor['clip'][1])

    def __getParamFromCache(self, typeCompactDescr, paramName, default = None):
        itemTypeID, nationID, typeID = vehicles.parseIntCompactDescr(typeCompactDescr)
        cachedParams = self.__cache.get(nationID, {}).get(itemTypeID, {}).get(typeCompactDescr, {})
        return cachedParams.get(paramName, default)

    def __precachEquipments(self):
        self.__cache.setdefault(nations.NONE_INDEX, {})[vehicles._EQUIPMENT] = {}
        equipments = self.__getItems(vehicles._EQUIPMENT, nations.NONE_INDEX)
        for eqpDescr in equipments:
            equipmentNations, params = set(), {}
            for vDescr in self.__getItems(vehicles._VEHICLE):
                if not eqpDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                    continue
                nation, id = vDescr.type.id
                equipmentNations.add(nation)

            eqDescrType = type(eqpDescr)
            if eqDescrType is artefacts.Artillery:
                shellDescr = vehicles.getDictDescr(eqpDescr.shellCompactDescr)
                shellParams = self.getShellParameters(shellDescr)
                params.update({'damage': (shellDescr['damage'][0], shellDescr['damage'][0]),
                 'piercingPower': eqpDescr.piercingPower,
                 'caliber': shellParams['caliber'],
                 'shotsNumberRange': eqpDescr.shotsNumber,
                 'areaRadius': eqpDescr.areaRadius,
                 'artDelayRange': eqpDescr.delay})
            elif eqDescrType is artefacts.Bomber:
                shellDescr = vehicles.getDictDescr(eqpDescr.shellCompactDescr)
                params.update({'bombDamage': (shellDescr['damage'][0], shellDescr['damage'][0]),
                 'piercingPower': eqpDescr.piercingPower,
                 'bombsNumberRange': eqpDescr.bombsNumber,
                 'areaSquare': eqpDescr.areaLength * eqpDescr.areaWidth,
                 'flyDelayRange': eqpDescr.delay})
            self.__cache[nations.NONE_INDEX][vehicles._EQUIPMENT][eqpDescr.compactDescr] = {'nations': equipmentNations,
             'avgParams': params}

    def __precachOptionalDevices(self):
        self.__cache.setdefault(nations.NONE_INDEX, {})[vehicles._OPTIONALDEVICE] = {}
        optDevs = self.__getItems(vehicles._OPTIONALDEVICE, nations.NONE_INDEX)
        for deviceDescr in optDevs:
            wmin, wmax = sys.maxint, -1
            deviceNations = set()
            for vDescr in self.__getItems(vehicles._VEHICLE):
                if not deviceDescr.checkCompatibilityWithVehicle(vDescr)[0]:
                    continue
                nation, id = vDescr.type.id
                deviceNations.add(nation)
                mods = deviceDescr.weightOnVehicle(vDescr)
                weightOnVehicle = math.ceil(vDescr.physics['weight'] * mods[0] + mods[1])
                wmin, wmax = min(wmin, weightOnVehicle), max(wmax, weightOnVehicle)

            self.__cache[nations.NONE_INDEX][vehicles._OPTIONALDEVICE][deviceDescr.compactDescr] = {'weight': (wmin, wmax),
             'nations': deviceNations}

    def __precachGuns(self):
        for nationName, nationIdx in nations.INDICES.iteritems():
            self.__cache.setdefault(nationIdx, {})[vehicles._GUN] = {}
            vcls = self.__getItems(vehicles._VEHICLE, nationIdx)
            guns = self.__getItems(vehicles._GUN, nationIdx)
            for g in guns:
                descriptors = list()
                cacheParams = {'turrets': list(),
                 'avgParams': dict(),
                 CLIP_VEHICLES_PROP_NAME: list()}
                clipVehiclesDict = dict()
                for vDescr in vcls:
                    for vTurrets in vDescr.type.turrets:
                        for turret in vTurrets:
                            for gun in turret['guns']:
                                if gun['id'][1] == g['id'][1]:
                                    descriptors.append(gun)
                                    if len(vDescr.hull['fakeTurrets']['lobby']) != len(vDescr.turrets):
                                        turretString = turret['userString']
                                        cacheParams['turrets'].append(turretString)
                                    if gun['clip'][0] > 1:
                                        clipVehiclesDict[vDescr.type.compactDescr] = 0

                clipVehiclesList = []
                for key in clipVehiclesDict.iterkeys():
                    clipVehiclesList.append(key)

                cacheParams[CLIP_VEHICLES_PROP_NAME] = clipVehiclesList
                cacheParams['avgParams'] = self.__calcGunParams(g, descriptors)
                self.__cache[nationIdx][vehicles._GUN][g['compactDescr']] = cacheParams

    def __precachShells(self):
        for nationName, nationIdx in nations.INDICES.iteritems():
            self.__cache.setdefault(nationIdx, {})[vehicles._SHELL] = {}
            guns = self.__getItems(vehicles._GUN, nationIdx)
            shells = self.__getItems(vehicles._SHELL, nationIdx)
            for sDescr in shells:
                descriptors = list()
                gNames = list()
                self.__cache[nationIdx][vehicles._SHELL][sDescr['compactDescr']] = {'guns': list(),
                 'avgParams': dict()}
                for gDescr in guns:
                    if 'shots' in gDescr:
                        for shot in gDescr['shots']:
                            if shot['shell']['id'][1] == sDescr['id'][1]:
                                if gDescr['userString'] not in gNames:
                                    gNames.append(gDescr['userString'])
                                    descriptors.append(shot)

                self.__cache[nationIdx][vehicles._SHELL][sDescr['compactDescr']]['guns'] = gNames
                self.__cache[nationIdx][vehicles._SHELL][sDescr['compactDescr']]['avgParams'] = self.__calcShellParams(sDescr, descriptors)

    def __getComponentVehiclesNames(self, typeCompactDescr):
        from gui.shared.gui_items import getVehicleSuitablesByType
        itemTypeIdx, nationIdx, typeIdx = vehicles.parseIntCompactDescr(typeCompactDescr)
        result = list()
        for vDescr in self.__getItems(vehicles._VEHICLE, nationIdx):
            components, _ = getVehicleSuitablesByType(vDescr, itemTypeIdx)
            filtered = filter(lambda item: item['compactDescr'] == typeCompactDescr, components)
            if len(filtered):
                result.append(vDescr.type.userString)

        return result

    def init(self):
        import time
        startTime = time.time()
        self.__init = False
        try:
            self.__xmlItems = self.__readXMLItems()
            for itemTypeIdx, handler in self.__precachHandlers.iteritems():
                handler()

        except Exception:
            LOG_CURRENT_EXCEPTION()
            return False

        elapsed = time.time() - startTime
        LOG_DEBUG("Parameters' cache initialization has been completed. Time elapsed: %.5fs" % elapsed)
        self.__init = True
        return True

    def __calcGunParams(self, gunDescr, descriptors):
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
                self.__updateMinMaxValues(result, SHELL_RELOADING_TIME_PROP_NAME, descr['clip'][1])
                self.__updateMinMaxValues(result, RELOAD_MAGAZINE_TIME_PROP_NAME, descr[RELOAD_TIME_PROP_NAME])
                self.__updateMinMaxValues(result, SHELLS_COUNT_PROP_NAME, currShellsCount)
            self.__updateMinMaxValues(result, RELOAD_TIME_PROP_NAME, self._getShotsPerMinute(descr))
            curDispRadius = round(descr['shotDispersionAngle'] * 100, 2)
            curAimingTime = round(descr[AIMING_TIME_PROP_NAME], 1)
            self.__updateMinMaxValues(result, DISPERSION_RADIUS_PROP_NAME, curDispRadius)
            self.__updateMinMaxValues(result, AIMING_TIME_PROP_NAME, curAimingTime)

        if 'shots' in gunDescr:
            for shot in gunDescr['shots']:
                result[PIERCING_POWER_PROP_NAME].append('%d' % shot[PIERCING_POWER_PROP_NAME][0])
                result[DAMAGE_PROP_NAME].append('%d' % shot['shell'][DAMAGE_PROP_NAME][0])
                result[SHELLS_PROP_NAME].append(i18n.makeString('#item_types:shell/kinds/' + shot['shell']['kind']))

        return result

    def __updateMinMaxValues(self, targetDict, key, value):
        targetDict[key] = (min(targetDict[key][0], value), max(targetDict[key][1], value))

    def __calcShellParams(self, shellDescr, descriptors):
        result = {PIERCING_POWER_PROP_NAME: (sys.maxint, -1),
         DAMAGE_PROP_NAME: (sys.maxint, -1)}
        for d in descriptors:
            curPiercingPower = (round(d[PIERCING_POWER_PROP_NAME][0] - d[PIERCING_POWER_PROP_NAME][0] * d['shell']['piercingPowerRandomization']), round(d[PIERCING_POWER_PROP_NAME][0] + d[PIERCING_POWER_PROP_NAME][0] * d['shell']['piercingPowerRandomization']))
            curDamage = (round(d['shell'][DAMAGE_PROP_NAME][0] - d['shell'][DAMAGE_PROP_NAME][0] * d['shell']['damageRandomization']), round(d['shell'][DAMAGE_PROP_NAME][0] + d['shell'][DAMAGE_PROP_NAME][0] * d['shell']['damageRandomization']))
            result[PIERCING_POWER_PROP_NAME] = (min(result[PIERCING_POWER_PROP_NAME][0], curPiercingPower[0], curPiercingPower[1]), max(result[PIERCING_POWER_PROP_NAME][1], curPiercingPower[0], curPiercingPower[1]))
            result[DAMAGE_PROP_NAME] = (min(result[DAMAGE_PROP_NAME][0], curDamage[0], curDamage[1]), max(result[DAMAGE_PROP_NAME][1], curDamage[0], curDamage[1]))

        return result

    def getParameters(self, itemDescr, vehicleDescr = None):
        if isinstance(itemDescr, vehicles.VehicleDescr):
            itemTypeIdx = vehicles._VEHICLE
        else:
            itemTypeIdx, _, _ = vehicles.parseIntCompactDescr(itemDescr['compactDescr'])
        try:
            handler = self.__itemTypeHandlers.get(itemTypeIdx, lambda *args: None)
            return handler(itemDescr, vehicleDescr)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return dict()

    def getRadioParameters(self, itemDescr, _ = None):
        return {'radioDistance': int(round(itemDescr['distance'])),
         'weight': itemDescr['weight']}

    def getRadioCompatibles(self, itemDescr, _ = None):
        return {'vehicles': self.__getComponentVehiclesNames(itemDescr['compactDescr'])}

    def getChassisParameters(self, itemDescr, _ = None):
        return {'maxLoad': itemDescr['maxLoad'] / 1000,
         'rotationSpeed': int(round(180.0 / math.pi * itemDescr['rotationSpeed'], 0)),
         'weight': itemDescr['weight']}

    def getChassisCompatibles(self, itemDescr, _ = None):
        return {'vehicles': self.__getComponentVehiclesNames(itemDescr['compactDescr'])}

    def getEngineParameters(self, itemDescr, _ = None):
        return {'enginePower': int(round(itemDescr['power'] / vehicles.HP_TO_WATTS, 0)),
         'fireStartingChance': int(round(itemDescr['fireStartingChance'] * 100)),
         'weight': itemDescr['weight']}

    def getEngineCompatibles(self, itemDescr, vehicle = None):
        return {'vehicles': self.__getComponentVehiclesNames(itemDescr['compactDescr'])}

    def getTurretParameters(self, itemDescr, _ = None):
        return {'armor': itemDescr['primaryArmor'],
         'rotationSpeed': round(180.0 / math.pi * itemDescr['rotationSpeed']),
         'circularVisionRadius': itemDescr['circularVisionRadius'],
         'weight': itemDescr['weight']}

    def getTurretCompatibles(self, itemDescr, _ = None):
        return {'vehicles': self.__getComponentVehiclesNames(itemDescr['compactDescr']),
         'guns': [ gun['userString'] for gun in itemDescr['guns'] ]}

    def getVehicleParameters(self, vd, _ = None):
        pPower = (BigWorld.wg_getIntegralFormat(round(vd.shot[PIERCING_POWER_PROP_NAME][0] - vd.shot[PIERCING_POWER_PROP_NAME][0] * vd.shot['shell']['piercingPowerRandomization'])), BigWorld.wg_getIntegralFormat(round(vd.shot[PIERCING_POWER_PROP_NAME][0] + vd.shot[PIERCING_POWER_PROP_NAME][0] * vd.shot['shell']['piercingPowerRandomization'])))
        damage = (BigWorld.wg_getIntegralFormat(round(vd.shot['shell'][DAMAGE_PROP_NAME][0] - vd.shot['shell'][DAMAGE_PROP_NAME][0] * vd.shot['shell']['damageRandomization'])), BigWorld.wg_getIntegralFormat(round(vd.shot['shell'][DAMAGE_PROP_NAME][0] + vd.shot['shell'][DAMAGE_PROP_NAME][0] * vd.shot['shell']['damageRandomization'])))
        weight = (vd.physics['weight'] / 1000, vd.miscAttrs['maxWeight'] / 1000)
        enginePower = round(vd.physics['enginePower'] / vehicles.HP_TO_WATTS)
        shotsPerMinute = self._getShotsPerMinute(vd.gun)
        explosionRadius = round(vd.shot['shell']['explosionRadius'], 2) if vd.shot['shell']['kind'] == 'HIGH_EXPLOSIVE' else 0
        return {'maxHealth': vd.maxHealth,
         'weight': weight,
         'enginePower': enginePower,
         'enginePowerPerTon': round(enginePower / weight[0], 2),
         'speedLimits': round(vd.physics['speedLimits'][0] * 3.6, 2),
         'chassisRotationSpeed': round(180 / math.pi * vd.chassis['rotationSpeed'], 0),
         'hullArmor': vd.hull['primaryArmor'],
         DAMAGE_PROP_NAME: damage,
         'damageAvg': vd.shot['shell'][DAMAGE_PROP_NAME][0],
         'damageAvgPerMinute': round(shotsPerMinute * vd.shot['shell'][DAMAGE_PROP_NAME][0]),
         PIERCING_POWER_PROP_NAME: pPower,
         RELOAD_TIME_PROP_NAME: self._getShotsPerMinute(vd.gun),
         'turretRotationSpeed': round(180.0 / math.pi * vd.turret['rotationSpeed']),
         'gunRotationSpeed': round(180.0 / math.pi * vd.turret['rotationSpeed']),
         'circularVisionRadius': vd.turret['circularVisionRadius'],
         'radioDistance': vd.radio['distance'],
         'turretArmor': vd.turret['primaryArmor'],
         'explosionRadius': explosionRadius,
         AIMING_TIME_PROP_NAME: round(vd.gun[AIMING_TIME_PROP_NAME], 1),
         'shotDispersionAngle': round(vd.gun['shotDispersionAngle'] * 100, 2),
         'reloadTimeSecs': round(self.__SEC_IN_MINUTE / shotsPerMinute)}

    def getEquipmentParameters(self, itemDescr, _ = None):
        intCD = itemDescr['compactDescr']
        result = {'nations': self.__getParamFromCache(intCD, 'nations', default=nations.INDICES.values())}
        result.update(self.__getParamFromCache(intCD, 'avgParams', default={}))
        return result

    def getOptionalDeviceParameters(self, itemDescr, vehicleDescr = None):
        weight = 0
        optNations = ()
        index = None
        if vehicleDescr is not None:
            try:
                if itemDescr in vehicleDescr.optionalDevices:
                    index = vehicleDescr.optionalDevices.index(itemDescr)
                    vehicleDescr.removeOptionalDevice(index)
                mods = itemDescr.weightOnVehicle(vehicleDescr)
                weight = math.ceil(vehicleDescr.physics['weight'] * mods[0] + mods[1])
                weight = (weight, weight)
                if index is not None:
                    vehicleDescr.installOptionalDevice(itemDescr['compactDescr'], index)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        else:
            weight = self.__getParamFromCache(itemDescr['compactDescr'], 'weight', default=0)
            optNations = self.__getParamFromCache(itemDescr['compactDescr'], 'nations', default=nations.INDICES.values())
        return {'weight': weight,
         'nations': optNations}

    def getGunParameters(self, itemDescr, vehicleDescr = None):
        avgParams = dict(self.__getParamFromCache(itemDescr['compactDescr'], 'avgParams', default={}))
        if vehicleDescr is not None:
            try:
                descriptors = []
                for gun in vehicleDescr.turret['guns']:
                    if gun['id'][1] == itemDescr['id'][1]:
                        descriptors.append(gun)

                if not descriptors:
                    for vTurrets in vehicleDescr.type.turrets:
                        for turret in vTurrets:
                            for gun in turret['guns']:
                                if gun['id'][1] == itemDescr['id'][1]:
                                    descriptors.append(gun)

                avgParams = self.__calcGunParams(itemDescr, descriptors)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        return {'caliber': itemDescr['shots'][0]['shell']['caliber'],
         SHELLS_COUNT_PROP_NAME: avgParams[SHELLS_COUNT_PROP_NAME],
         SHELL_RELOADING_TIME_PROP_NAME: avgParams[SHELL_RELOADING_TIME_PROP_NAME],
         RELOAD_MAGAZINE_TIME_PROP_NAME: avgParams[RELOAD_MAGAZINE_TIME_PROP_NAME],
         RELOAD_TIME_PROP_NAME: avgParams[RELOAD_TIME_PROP_NAME],
         'avgPiercingPower': avgParams[PIERCING_POWER_PROP_NAME],
         'avgDamage': avgParams[DAMAGE_PROP_NAME],
         'dispertionRadius': avgParams[DISPERSION_RADIUS_PROP_NAME],
         AIMING_TIME_PROP_NAME: avgParams[AIMING_TIME_PROP_NAME],
         'weight': itemDescr['weight']}

    def getGunCompatibles(self, itemDescr, _ = None):
        avgParams = dict(self.__getParamFromCache(itemDescr['compactDescr'], 'avgParams', default={}))
        allVehiclesNames = self.__getComponentVehiclesNames(itemDescr['compactDescr'])
        clipVehiclesCD_List = self.__getParamFromCache(itemDescr['compactDescr'], CLIP_VEHICLES_PROP_NAME, default=tuple())
        normalVehicles = []
        clipVehiclesNames = []
        for clipV_CD in clipVehiclesCD_List:
            userFriendlyVehicleName = getVehicleType(clipV_CD).userString
            clipVehiclesNames.append(userFriendlyVehicleName)
            if userFriendlyVehicleName in allVehiclesNames:
                allVehiclesNames.remove(userFriendlyVehicleName)

        return {'vehicles': allVehiclesNames,
         SHELLS_PROP_NAME: avgParams.get(SHELLS_PROP_NAME, tuple()),
         'turrets': self.__getParamFromCache(itemDescr['compactDescr'], 'turrets', default=tuple()),
         CLIP_VEHICLES_PROP_NAME: clipVehiclesNames,
         CLIP_VEHICLES_CD_PROP_NAME: clipVehiclesCD_List}

    def getShellParameters(self, itemDescr, vehicleDescr = None):
        avgParams = self.__getParamFromCache(itemDescr['compactDescr'], 'avgParams', default={})
        if vehicleDescr is not None:
            try:
                descriptors = []
                for turrets in vehicleDescr.type.turrets:
                    for turret in turrets:
                        for gun in turret['guns']:
                            if 'shots' in gun:
                                for shot in gun['shots']:
                                    if shot['shell']['id'][1] == itemDescr['id'][1]:
                                        if gun == vehicleDescr.gun:
                                            descriptors.append(shot)

                avgParams = self.__calcShellParams(itemDescr, descriptors)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        return {'caliber': itemDescr['caliber'],
         PIERCING_POWER_PROP_NAME: avgParams[PIERCING_POWER_PROP_NAME],
         DAMAGE_PROP_NAME: avgParams[DAMAGE_PROP_NAME],
         'explosionRadius': itemDescr['explosionRadius'] if itemDescr['kind'] == 'HIGH_EXPLOSIVE' else 0}

    def getShellCompatibles(self, itemDescr, _ = None):
        return {'shellGuns': self.__getParamFromCache(itemDescr['compactDescr'], 'guns', default=tuple())}

    def getGunReloadingSystemType(self, itemCD, vehicleCD = None):
        reloadingType = GUN_NORMAL
        VCDList = self.__getParamFromCache(itemCD, CLIP_VEHICLES_PROP_NAME, default=tuple())
        if VCDList:
            reloadingType = GUN_CAN_BE_CLIP
            if vehicleCD is not None and vehicleCD in VCDList:
                reloadingType = GUN_CLIP
            elif vehicleCD is not None:
                reloadingType = GUN_NORMAL
        return reloadingType


g_instance = _ParametersCache()
