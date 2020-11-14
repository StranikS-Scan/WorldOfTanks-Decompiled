# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/battle_royale/params.py
import logging
from collections import namedtuple
from gui import makeHtmlString, GUI_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_royale.constants import ParamTypes
from gui.doc_loaders.battle_royale_settings_loader import getTreeModuleSettings, getTreeVehicleParams
from gui.impl.backport.backport_system_locale import getNiceNumberFormat
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import formatters as params_formatters
from gui.shared.items_parameters import params as base_params
from gui.shared.items_parameters.comparator import ItemsComparator, PARAM_STATE, getParamExtendedData
from gui.shared.items_parameters.formatters import FORMAT_SETTINGS, MEASURE_UNITS
from gui.shared.items_parameters import params_helper
from helpers import i18n, dependency
from items import ITEM_TYPES
from items import getTypeOfCompactDescr
from skeletons.gui.shared.gui_items import IGuiItemsFactory
_logger = logging.getLogger(__name__)
_ModuleDescr = namedtuple('_ModuleDescr', ('vDescr', 'currentModuleDescr', 'intCD', 'typeCD', 'moduleParams'))
ROYALE_VISIBILITY_PARAMS = ('radarRadius', 'radarCooldown')
_ROYALE_MOBILITY_PARAMS = ('forwardMaxSpeed', 'chassisModuleRotationSpeed', 'turretModuleRotationSpeed')
_ROYALE_GUN_PARAMS = ('gunModuleAvgDamageList',)
_BACKWARD_QUALITY_PARAMS = ('radarCooldown', 'hullWeight', 'hullAndChassisWeight')
_PARAMS_GROUPS = (_ROYALE_GUN_PARAMS + params_helper.RELATIVE_POWER_PARAMS,
 params_helper.RELATIVE_ARMOR_PARAMS,
 params_helper.RELATIVE_MOBILITY_PARAMS + _ROYALE_MOBILITY_PARAMS,
 params_helper.RELATIVE_CAMOUFLAGE_PARAMS,
 ROYALE_VISIBILITY_PARAMS + params_helper.RELATIVE_VISIBILITY_PARAMS)

class _RadioParams(base_params.RadioParams):

    @property
    def radarRadius(self):
        return self._itemDescr.radarRadius

    @property
    def radarCooldown(self):
        return self._itemDescr.radarCooldown


class _TurretParams(base_params.TurretParams):

    @property
    def maxHealth(self):
        return self._itemDescr.maxHealth


class _ChassisParams(base_params.ChassisParams):

    @property
    def maxHullHealth(self):
        hull = self.__getVariantHull()
        return hull.maxHealth if hull else self._itemDescr.maxHealth

    @property
    def hullWeight(self):
        hull = self.__getVariantHull()
        return hull.weight if hull else self._vehicleDescr.hull.weight

    @property
    def hullAndChassisWeight(self):
        return self.hullWeight + self.weight

    @property
    def hullArmor(self):
        hull = self.__getVariantHull()
        return hull.primaryArmor if hull else self._vehicleDescr.hull.primaryArmor

    def __getVariantHull(self):
        _, innationItemID = self._itemDescr.id
        vehicleHulls = self._vehicleDescr.type
        for hull in vehicleHulls.hulls:
            variantMatch = hull.variantMatch
            if variantMatch:
                if innationItemID == variantMatch[0]:
                    return hull

        return None


class _VehicleParams(base_params.VehicleParams):

    @property
    def chassisModuleRotationSpeed(self):
        params = self.__getModuleByType(ITEM_TYPES.vehicleChassis, self._itemDescr.chassis)
        return params.rotationSpeed if not params.isWheeled else None

    @property
    def hullAndChassisWeight(self):
        params = self.__getModuleByType(ITEM_TYPES.vehicleChassis, self._itemDescr.chassis)
        return params.hullAndChassisWeight

    @property
    def turretModuleRotationSpeed(self):
        params = self.__getModuleByType(ITEM_TYPES.vehicleTurret, self._itemDescr.turret)
        return params.rotationSpeed

    @property
    def gunModuleAvgDamageList(self):
        params = self.__getModuleByType(ITEM_TYPES.vehicleGun, self._itemDescr.gun)
        return params.avgDamageList

    @property
    def radarCooldown(self):
        return self._itemDescr.radio.radarCooldown

    @property
    def radarRadius(self):
        return self._itemDescr.radio.radarRadius

    @property
    def forwardMaxSpeed(self):
        return self._itemDescr.type.xphysics['engines'][self._itemDescr.engine.name]['smplFwMaxSpeed']

    def __getModuleByType(self, mType, moduleDescr):
        return _ITEM_TYPE_HANDLERS[mType](moduleDescr, self._itemDescr)


class _BRItemsComparator(ItemsComparator):

    def getExtendedData(self, paramName):
        isInvertedValue = paramName in _BACKWARD_QUALITY_PARAMS or None
        return getParamExtendedData(paramName, self._currentParams.get(paramName), self._otherParams.get(paramName), self._getPenaltiesAndBonuses(paramName), customQualityParams=isInvertedValue)


_ITEM_TYPE_HANDLERS = {ITEM_TYPES.vehicleRadio: _RadioParams,
 ITEM_TYPES.vehicleEngine: base_params.EngineParams,
 ITEM_TYPES.vehicleChassis: _ChassisParams,
 ITEM_TYPES.vehicleTurret: _TurretParams,
 ITEM_TYPES.vehicleGun: base_params.GunParams}

def _updateSeparator(separator):
    space = ' '
    return ''.join((space, text_styles.mainBig(separator), space))


def _reloadTimeSecsPreprocessor(value, states):
    statesOverride = states
    if states:
        statesOverride = list()
        stateOverride = states[0][0]
        for state in states:
            stateCopy = list(state)
            stateCopy[0] = stateOverride
            statesOverride.append(stateCopy)

    return (value, None, statesOverride)


def _autoReloadPreprocessor(reloadTimes, rowStates):
    result = params_formatters._autoReloadPreprocessor(reloadTimes, rowStates)
    result = list(result)
    result[1] = _updateSeparator(result[1])
    states = result[2]
    if states:
        result[2] = ((PARAM_STATE.NORMAL, 0),) * len(states)
    return result


def _generateSettings():
    s = {'radarRadius': params_formatters._niceFormat,
     'radarCooldown': params_formatters._niceFormat,
     'maxHullHealth': params_formatters._integralFormat,
     'hullWeight': params_formatters._niceRangeFormat,
     'hullAndChassisWeight': params_formatters._niceRangeFormat,
     'forwardMaxSpeed': params_formatters._niceFormat}
    s.update(FORMAT_SETTINGS)
    s['reloadTimeSecs'] = s.get('reloadTimeSecs', {}).copy()
    s['reloadTimeSecs']['preprocessor'] = _reloadTimeSecsPreprocessor
    s[params_formatters.AUTO_RELOAD_PROP_NAME] = {'preprocessor': _autoReloadPreprocessor,
     'rounder': lambda v: getNiceNumberFormat(round(v, 1))}
    return s


_FORMAT_SETTINGS = _generateSettings()

def _getParameters(typeCD, module, vDescr=None):
    itemParams = _ITEM_TYPE_HANDLERS[typeCD](module.descriptor, vDescr)
    return itemParams.getParamsDict() if GUI_SETTINGS.technicalInfo else {}


def _getModuleDescr(module, vehicle):
    vDescr = vehicle.descriptor
    currModuleDescr, _ = vDescr.getComponentsByType(module.itemTypeName)
    intCD = currModuleDescr.compactDescr
    typeCD = getTypeOfCompactDescr(intCD)
    return _ModuleDescr(vDescr=vDescr, currentModuleDescr=currModuleDescr, intCD=intCD, typeCD=typeCD, moduleParams=_getParameters(typeCD, module, vDescr))


@dependency.replace_none_kwargs(factory=IGuiItemsFactory)
def _getCurrentModule(moduleDescr, factory=None):
    return factory.createGuiItem(moduleDescr.typeCD, intCompactDescr=moduleDescr.intCD)


def _itemsComparator(typeCD, currentItemParams, otherItem, vehicleDescr=None):
    return _BRItemsComparator(currentItemParams, _getParameters(typeCD, otherItem, vehicleDescr))


def _makeTxtForNormal(text):
    return _makeTxt(text, 'paramTitleWhite')


def _makeTxtForWorse(text):
    return _makeTxt(text, 'paramTitleRed')


def _makeTxtForBetter(text):
    return _makeTxt(text, 'paramTitleGreen')


def _standardText(text):
    return _makeTxt(i18n.makeString(text), 'standardText')


def _makeTxt(text, key):
    return makeHtmlString('html_templates:battleRoyale', key, ctx={'message': text})


def _formatModuleParamName(paramName):
    builder = text_styles.builder()
    resource = R.strings.menu.moduleInfo.params
    paramMsgId = backport.msgid(resource.dyn(paramName)()) if resource.dyn(paramName) else None
    builder.addStyledText(text_styles.main, paramMsgId)
    builder.addStyledText(_standardText, MEASURE_UNITS.get(paramName, ''))
    return builder.render()


def _deltaWrapper(fn):

    def wrapped(paramValue):
        formattedValue = fn(paramValue)
        return '+%s' % formattedValue if isinstance(paramValue, (int, float)) and paramValue > 0 else formattedValue

    return wrapped


def _generateFormatSettings(rounder=None):
    copy = {}
    for originalName, originalSetting in _FORMAT_SETTINGS.iteritems():
        settingCopy = originalSetting.copy()
        if 'separator' in settingCopy:
            settingCopy['separator'] = _updateSeparator(settingCopy['separator'])
        if rounder:
            sRounder = settingCopy['rounder']
            settingCopy['rounder'] = rounder(sRounder)
        copy[originalName] = settingCopy

    return copy


_CMP_FORMAT_SETTINGS = _generateFormatSettings()
_CMP_FORMAT_DELTA_SETTINGS = _generateFormatSettings(_deltaWrapper)
_DELTA_SCHEME = (_makeTxtForWorse, _makeTxtForNormal, _makeTxtForBetter)

def getModuleParameters(module, vehicle, currentModule=None):
    moduleDescr = _getModuleDescr(module, vehicle)
    currModule = currentModule if currentModule is not None else _getCurrentModule(moduleDescr)
    comparator = _itemsComparator(moduleDescr.typeCD, moduleDescr.moduleParams, currModule, moduleDescr.vDescr)
    params = []
    moduleData = getTreeModuleSettings(module)
    deltaParamsList = moduleData.deltaParams if moduleData is not None else tuple()
    for paramName in deltaParamsList:
        if paramName in moduleDescr.moduleParams:
            paramInfo = comparator.getExtendedData(paramName)
            fmtValue = params_formatters.formatParameterDelta(paramInfo, _DELTA_SCHEME, _CMP_FORMAT_DELTA_SETTINGS)
            if fmtValue is not None:
                params.append({'value': str(fmtValue),
                 'description': _formatModuleParamName(paramName)})

    paramsList = moduleData.params if moduleData is not None else []
    for paramName in paramsList:
        if paramName in moduleDescr.moduleParams:
            paramInfo = comparator.getExtendedData(paramName)
            fmtValue = params_formatters.formatParameter(paramName, paramInfo.value, paramInfo.state, _DELTA_SCHEME, _CMP_FORMAT_SETTINGS)
            if fmtValue is not None:
                params.append({'value': str(fmtValue),
                 'description': _formatModuleParamName(paramName)})

    paramsDict = moduleData.constParams if moduleData else {}
    for paramName, paramVal in paramsDict.iteritems():
        fmtValue = _makeTxtForBetter(paramVal)
        params.append({'value': str(fmtValue),
         'description': _formatModuleParamName(paramName)})

    return params


def getVehicleParameters(vehicle):
    vehicleParams = _VehicleParams(vehicle).getParamsDict() if GUI_SETTINGS.technicalInfo else {}
    params = []
    paramsList = getTreeVehicleParams()
    for paramGroup in _PARAMS_GROUPS:
        group = []
        for paramName in paramGroup:
            if paramName in paramsList:
                fmtValue = params_formatters.formatParameter(paramName, vehicleParams.get(paramName))
                if fmtValue is not None:
                    group.append({'value': str(fmtValue),
                     'description': params_formatters.formatVehicleParamName(paramName),
                     'isLastInGroup': False})
                else:
                    _logger.warning("Couldn't format value for %s", paramName)

        if group:
            group[-1]['isLastInGroup'] = True
            params.extend(group)

    return params


def getShortListParameters(module, vehicle, currentModule=None, moduleData=None, moduleDescr=None):
    if moduleData is None:
        moduleData = getTreeModuleSettings(module)
    if moduleDescr is None:
        moduleDescr = _getModuleDescr(module, vehicle)
    params = []
    priorityParamsList = moduleData.priorityParams if moduleData else []
    if not priorityParamsList:
        return params
    else:
        currModule = currentModule if currentModule is not None else _getCurrentModule(moduleDescr)
        comparator = _itemsComparator(moduleDescr.typeCD, moduleDescr.moduleParams, currModule, moduleDescr.vDescr)
        for paramName, paramType in priorityParamsList:
            formattedParam = _formatParameters(paramType, paramName, moduleData, comparator)
            if formattedParam is not None:
                params.append(formattedParam)

        return params


def _formatParameters(paramType, paramName, moduleData, comparator):
    fmtValue = None
    if paramType == ParamTypes.CONST:
        paramVal = moduleData.constParams[paramName]
        fmtValue = _makeTxtForBetter(paramVal)
    else:
        paramInfo = comparator.getExtendedData(paramName)
        if paramType == ParamTypes.SIMPLE:
            fmtValue = params_formatters.formatParameter(paramName, paramInfo.value, paramInfo.state, _DELTA_SCHEME, _CMP_FORMAT_SETTINGS)
        elif paramType == ParamTypes.DELTA:
            fmtValue = params_formatters.formatParameterDelta(paramInfo, _DELTA_SCHEME, _CMP_FORMAT_DELTA_SETTINGS)
    return {'value': str(fmtValue),
     'description': _formatModuleParamName(paramName)} if fmtValue is not None else None
