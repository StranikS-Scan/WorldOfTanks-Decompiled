# Embedded file name: scripts/client/gui/shared/utils/ItemsParameters.py
import BigWorld
from gui.shared.utils import ParametersCache, RELOAD_TIME_PROP_NAME, AIMING_TIME_PROP_NAME, PIERCING_POWER_PROP_NAME, DAMAGE_PROP_NAME, SHELLS_COUNT_PROP_NAME, SHELL_RELOADING_TIME_PROP_NAME, RELOAD_MAGAZINE_TIME_PROP_NAME, CLIP_VEHICLES_PROP_NAME, GUN_RELOADING_TYPE, GUN_NORMAL, GUN_CAN_BE_CLIP, GUN_CLIP, CLIP_VEHICLES_CD_PROP_NAME, UNICHARGED_VEHICLES_PROP_NAME, VEHICLES_PROP_NAME
from debug_utils import *
from gui import GUI_SETTINGS
from items import vehicles, getTypeInfoByIndex, getTypeOfCompactDescr, artefacts

class _ItemsParameters(object):

    def __init__(self):
        self.__itemTypeHandlers = {vehicles._RADIO: self.getRadio,
         vehicles._ENGINE: self.getEngine,
         vehicles._CHASSIS: self.getChassis,
         vehicles._TURRET: self.getTurret,
         vehicles._VEHICLE: self.getVehicle,
         vehicles._EQUIPMENT: self.getEquipment,
         vehicles._OPTIONALDEVICE: self.getOptionalDevice,
         vehicles._GUN: self.getGun,
         vehicles._SHELL: self.getShell}
        self.__itemCommonParamsList = {vehicles._RADIO: ('radioDistance', ('weight', lambda v: BigWorld.wg_getIntegralFormat(v))),
         vehicles._CHASSIS: (('maxLoad', lambda v: BigWorld.wg_getNiceNumberFormat(v)), 'rotationSpeed', ('weight', lambda v: BigWorld.wg_getIntegralFormat(v))),
         vehicles._ENGINE: (('enginePower', lambda v: BigWorld.wg_getIntegralFormat(v)), ('fireStartingChance', lambda v: '%d%%' % v), ('weight', lambda v: BigWorld.wg_getIntegralFormat(v))),
         vehicles._TURRET: (('armor', lambda v: self.__formatList(v)),
                            ('rotationSpeed', lambda v: BigWorld.wg_getIntegralFormat(v)),
                            ('circularVisionRadius', lambda v: BigWorld.wg_getIntegralFormat(v)),
                            ('weight', lambda v: BigWorld.wg_getIntegralFormat(v))),
         vehicles._VEHICLE: (('maxHealth', lambda v: BigWorld.wg_getIntegralFormat(v)),
                             ('weight', lambda v: self.__formatList(v, False)),
                             ('enginePower', lambda v: BigWorld.wg_getIntegralFormat(v)),
                             ('speedLimits', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                             ('chassisRotationSpeed', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                             ('hullArmor', lambda v: self.__formatList(v)),
                             ('turretArmor', lambda v: self.__formatList(v)),
                             (DAMAGE_PROP_NAME, lambda v: '%s-%s' % v),
                             (PIERCING_POWER_PROP_NAME, lambda v: '%s-%s' % v),
                             (RELOAD_TIME_PROP_NAME, lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                             ('turretRotationSpeed', lambda v: BigWorld.wg_getIntegralFormat(v)),
                             ('gunRotationSpeed', lambda v: BigWorld.wg_getIntegralFormat(v)),
                             ('circularVisionRadius', lambda v: BigWorld.wg_getIntegralFormat(v)),
                             ('radioDistance', lambda v: BigWorld.wg_getIntegralFormat(v))),
         vehicles._EQUIPMENT: {artefacts.Artillery: (('damage', lambda v: self.__formatRange(*v)),
                                                     ('piercingPower', lambda v: self.__formatRange(*v)),
                                                     ('caliber', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                                                     ('shotsNumberRange', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                                                     ('areaRadius', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                                                     ('artDelayRange', lambda v: BigWorld.wg_getNiceNumberFormat(v))),
                               artefacts.Bomber: (('bombDamage', lambda v: self.__formatRange(*v)),
                                                  ('piercingPower', lambda v: self.__formatRange(*v)),
                                                  ('bombsNumberRange', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                                                  ('areaSquare', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                                                  ('flyDelayRange', lambda v: BigWorld.wg_getNiceNumberFormat(v)))},
         vehicles._SHELL: (('caliber', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                           (PIERCING_POWER_PROP_NAME, lambda v: self.__formatRange(*v)),
                           (DAMAGE_PROP_NAME, lambda v: self.__formatRange(*v)),
                           ('explosionRadius', lambda v: (BigWorld.wg_getNiceNumberFormat(v) if v > 0 else None))),
         vehicles._OPTIONALDEVICE: (('weight', lambda v: (self.__formatRange(*v) if v[1] > 0 else None)),),
         vehicles._GUN: (('caliber', lambda v: BigWorld.wg_getNiceNumberFormat(v)),
                         (SHELLS_COUNT_PROP_NAME, lambda v: self.__formatRange(*v)),
                         (SHELL_RELOADING_TIME_PROP_NAME, lambda v: self.__formatRange(*v)),
                         (RELOAD_MAGAZINE_TIME_PROP_NAME, lambda v: self.__formatRange(*v)),
                         (RELOAD_TIME_PROP_NAME, lambda v: self.__formatRange(*v)),
                         ('avgPiercingPower', lambda v: self.__formatList(v)),
                         ('avgDamage', lambda v: self.__formatList(v)),
                         ('dispertionRadius', lambda v: self.__formatRange(*v)),
                         (AIMING_TIME_PROP_NAME, lambda v: self.__formatRange(*v)),
                         ('weight', lambda v: BigWorld.wg_getIntegralFormat(v)))}

    def __getCommonParameters(self, itemTypeCompDescr, paramsDict, excluded = tuple()):
        result = list()
        if GUI_SETTINGS.technicalInfo:
            compDescrType = getTypeOfCompactDescr(itemTypeCompDescr)
            params = self.__itemCommonParamsList.get(compDescrType, {})
            if compDescrType == vehicles._EQUIPMENT:
                eqDescr = vehicles.getDictDescr(itemTypeCompDescr)
                params = params.get(type(eqDescr), [])
            else:
                params = self.__itemCommonParamsList.get(compDescrType, [])
            for param in params:
                if type(param) == str:
                    if param not in excluded:
                        result.append([param, paramsDict.get(param)])
                else:
                    paramName = param[0]
                    paramValue = paramsDict.get(param[0])
                    formatFunc = param[1]
                    formattedValue = formatFunc(paramValue)
                    if formattedValue is not None and paramName not in excluded:
                        result.append([paramName, formattedValue])

        return result

    def __formatAsCurrent(self, item):
        return '<font color="#658c4c"><b>%s</b></font>' % item

    def __formatRange(self, minVal, maxVal):
        if minVal == maxVal:
            return BigWorld.wg_getNiceNumberFormat(minVal)

        def smartRound(value):
            if value > 99:
                return round(value)
            elif value > 9:
                return round(value, 1)
            else:
                return round(value, 2)

        return '%s-%s' % (BigWorld.wg_getNiceNumberFormat(smartRound(minVal)), BigWorld.wg_getNiceNumberFormat(smartRound(maxVal)))

    def __formatList(self, values, isIntegral = True):
        wrapper = BigWorld.wg_getNiceNumberFormat
        if isIntegral:
            wrapper = lambda v: BigWorld.wg_getIntegralFormat(int(v))
        return '/'.join(map(lambda v: wrapper(v), values))

    def __getCompatibles(self, name, collection):
        return ', '.join([ (self.__formatAsCurrent(c) if c == name else c) for c in collection ])

    def __getItemFullName(self, itemTypeIdx, itemDescr):
        return getTypeInfoByIndex(itemTypeIdx)['userString'] + ' ' + itemDescr['userString']

    def getParameters(self, itemDescr, vehicleDescr = None):
        return self.__get(itemDescr, vehicleDescr, isCompatibles=False).get('parameters')

    def getCompatibles(self, itemDescr, vehicleDescr = None):
        return self.__get(itemDescr, vehicleDescr, isParameters=False).get('compatible')

    def get(self, itemDescr, vehicleDescr = None):
        return self.__get(itemDescr, vehicleDescr)

    def __get(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        try:
            compactDescr = itemDescr.type.compactDescr if isinstance(itemDescr, vehicles.VehicleDescr) else itemDescr['compactDescr']
            handler = self.__itemTypeHandlers.get(getTypeOfCompactDescr(compactDescr), lambda *args: None)
            return handler(itemDescr, vehicleDescr, isParameters, isCompatibles)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return dict()

    def getRadio(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getRadioParameters(itemDescr, vehicleDescr))
        if isCompatibles:
            curVehicle = None
            if vehicleDescr and vehicleDescr.radio['id'][1] == itemDescr['id'][1]:
                curVehicle = vehicleDescr.type.userString
            compatibles = ParametersCache.g_instance.getRadioCompatibles(itemDescr, vehicleDescr)
            result['compatible'] = (('vehicles', self.__getCompatibles(curVehicle, compatibles['vehicles'])),)
        return result

    def getChassis(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getChassisParameters(itemDescr, vehicleDescr))
        if isCompatibles:
            curVehicle = None
            if vehicleDescr and vehicleDescr.chassis['id'][1] == itemDescr['id'][1]:
                curVehicle = vehicleDescr.type.userString
            compatibles = ParametersCache.g_instance.getChassisCompatibles(itemDescr, vehicleDescr)
            result['compatible'] = (('vehicles', self.__getCompatibles(curVehicle, compatibles['vehicles'])),)
        return result

    def getEngine(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getEngineParameters(itemDescr, vehicleDescr))
        if isCompatibles:
            curVehicle = None
            if vehicleDescr and vehicleDescr.engine['id'][1] == itemDescr['id'][1]:
                curVehicle = vehicleDescr.type.userString
            compatibles = ParametersCache.g_instance.getEngineCompatibles(itemDescr, vehicleDescr)
            result['compatible'] = (('vehicles', self.__getCompatibles(curVehicle, compatibles['vehicles'])),)
        return result

    def getTurret(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getTurretParameters(itemDescr, vehicleDescr))
        if isCompatibles:
            curVehicle = curGun = None
            if vehicleDescr and vehicleDescr.turret['id'][1] == itemDescr['id'][1]:
                curGun = vehicleDescr.gun['userString']
                curVehicle = vehicleDescr.type.userString
            compatibles = ParametersCache.g_instance.getTurretCompatibles(itemDescr, vehicleDescr)
            result['compatible'] = (('vehicles', self.__getCompatibles(curVehicle, compatibles['vehicles'])), ('guns', self.__getCompatibles(curGun, compatibles['guns'])))
        return result

    def getVehicle(self, vehicleDescr, stubParameter = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple(),
         'stats': list(),
         'base': list()}
        vehicleHasTurrets = len(vehicleDescr.hull['fakeTurrets']['lobby']) != len(vehicleDescr.turrets)
        if isParameters:
            excluded = list()
            if not vehicleHasTurrets:
                excluded.append('turretArmor')
            if not vehicleHasTurrets:
                excluded.append('turretRotationSpeed')
            else:
                excluded.append('gunRotationSpeed')
            result['parameters'] = self.__getCommonParameters(vehicleDescr.type.compactDescr, ParametersCache.g_instance.getVehicleParameters(vehicleDescr), excluded)
        if True:
            result['base'] = [self.__getItemFullName(vehicles._GUN, vehicleDescr.gun),
             self.__getItemFullName(vehicles._ENGINE, vehicleDescr.engine),
             self.__getItemFullName(vehicles._CHASSIS, vehicleDescr.chassis),
             self.__getItemFullName(vehicles._RADIO, vehicleDescr.radio)]
            if vehicleHasTurrets:
                result['base'].insert(1, self.__getItemFullName(vehicles._TURRET, vehicleDescr.turret))
        return result

    def getEquipment(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getEquipmentParameters(itemDescr, vehicleDescr))
        if isCompatibles:
            pass
        return result

    def getOptionalDevice(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getOptionalDeviceParameters(itemDescr, vehicleDescr))
        if isCompatibles:
            pass
        return result

    def getGun(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isCompatibles:
            compatibles = ParametersCache.g_instance.getGunCompatibles(itemDescr, vehicleDescr)
            clipVehicleNamesList = compatibles[CLIP_VEHICLES_PROP_NAME]
            vehiclesNamesList = compatibles['vehicles']
            curVehicle = curTurret = None
            if vehicleDescr and vehicleDescr.gun['id'][1] == itemDescr['id'][1]:
                curVehicle = vehicleDescr.type.userString
                curTurret = vehicleDescr.turret['userString']
            compatiblesResultList = []
            if len(vehiclesNamesList) == 0:
                compatiblesResultList.append((VEHICLES_PROP_NAME, self.__getCompatibles(curVehicle, clipVehicleNamesList)))
            else:
                isMixedRechargingType = len(clipVehicleNamesList) != 0
                compatiblesResultList.append((UNICHARGED_VEHICLES_PROP_NAME if isMixedRechargingType else VEHICLES_PROP_NAME, self.__getCompatibles(curVehicle, vehiclesNamesList)))
                if isMixedRechargingType:
                    compatiblesResultList.append((CLIP_VEHICLES_PROP_NAME, self.__getCompatibles(curVehicle, clipVehicleNamesList)))
            compatiblesResultList.append(('shells', ', '.join(compatibles['shells'])))
            result['compatible'] = compatiblesResultList
            if 'turrets' in result['compatible']:
                result['compatible'].insert(1, self.__getCompatibles(curTurret, compatibles['turrets']))
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getGunParameters(itemDescr, vehicleDescr))
            gunReloadingType = ParametersCache.g_instance.getGunReloadingSystemType(itemDescr['compactDescr'], vehicleDescr.type.compactDescr if vehicleDescr is not None else None)
            result['parameters'].append((GUN_RELOADING_TYPE, gunReloadingType))
        return result

    def __getGunReloadingSystemOpportunities(self, vehicleDescr, vehiclesNamesList, clipVehicleCdList):
        reloadingSystemType = GUN_NORMAL
        if vehicleDescr is not None:
            for vName in vehiclesNamesList:
                if vName == vehicleDescr.type.userString:
                    reloadingSystemType = GUN_NORMAL
                    return reloadingSystemType

        if len(clipVehicleCdList) > 0:
            reloadingSystemType = GUN_CAN_BE_CLIP
            if vehicleDescr is not None:
                for cVdescr in clipVehicleCdList:
                    if cVdescr == vehicleDescr.type.compactDescr:
                        reloadingSystemType = GUN_CLIP
                        break

            elif len(vehiclesNamesList) == 0:
                reloadingSystemType = GUN_CLIP
        return reloadingSystemType

    def getShell(self, itemDescr, vehicleDescr = None, isParameters = True, isCompatibles = True):
        result = {'parameters': tuple(),
         'compatible': tuple()}
        if isParameters:
            result['parameters'] = self.__getCommonParameters(itemDescr['compactDescr'], ParametersCache.g_instance.getShellParameters(itemDescr, vehicleDescr))
        if isCompatibles:
            compatibles = ParametersCache.g_instance.getShellCompatibles(itemDescr, vehicleDescr)
            result['compatible'] = (('shellGuns', ', '.join(compatibles['shellGuns'])),)
        return result


g_instance = _ItemsParameters()
