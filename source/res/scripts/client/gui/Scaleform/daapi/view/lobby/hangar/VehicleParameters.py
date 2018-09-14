# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/VehicleParameters.py
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.Scaleform.daapi.view.meta.VehicleParametersMeta import VehicleParametersMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.items_parameters import params_helper, MAX_RELATIVE_VALUE, formatters, RELATIVE_PARAMS
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.shared.formatters import text_styles
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.formatters import PARAMS_GROUPS

class VehicleParameters(VehicleParametersMeta):

    def __init__(self):
        super(VehicleParameters, self).__init__()
        self._vehParamsDP = None
        self._alreadyShowed = False
        self._paramsProviderCls = _VehParamsDataProvider
        self._expandedGroups = {'relativePower': AccountSettings.getSettings('relativePower'),
         'relativeArmor': AccountSettings.getSettings('relativeArmor'),
         'relativeMobility': AccountSettings.getSettings('relativeMobility'),
         'relativeVisibility': AccountSettings.getSettings('relativeVisibility'),
         'relativeCamouflage': AccountSettings.getSettings('relativeCamouflage')}
        return

    def changeVehParamsType(self):
        self._updateProviderType()
        self._vehParamsDP.rebuildList(self._getVehicleCache())

    def onParamClick(self, paramID):
        isOpened = not self._expandedGroups[paramID]
        AccountSettings.setSettings(paramID, isOpened)
        self._expandedGroups[paramID] = isOpened
        self._setDPUseAnimAndRebuild(False)

    def onListScroll(self):
        self._setDPUseAnimAndRebuild(False)

    def update(self, *args):
        self._vehParamsDP.setGroupsToShow(self._expandedGroups)
        self._setDPUseAnimAndRebuild(True)

    def _populate(self):
        super(VehicleParameters, self)._populate()
        g_settingsCore.onSettingsChanged += self.__onSettingsChange
        self._vehParamsDP = self._paramsProviderCls()
        self._vehParamsDP.setFlashObject(self.as_getDPS())
        self._updateProviderType()
        self.update()

    def _dispose(self):
        self._vehParamsDP.fini()
        self._vehParamsDP = None
        self._paramsProviderCls = None
        g_settingsCore.onSettingsChanged -= self.__onSettingsChange
        super(VehicleParameters, self)._dispose()
        return

    def _setDPUseAnimAndRebuild(self, useAnim):
        if self._vehParamsDP.useAnim != useAnim:
            self.as_setIsParamsAnimatedS(useAnim)
        self._vehParamsDP.setUseAnim(useAnim)
        self._vehParamsDP.rebuildList(self._getVehicleCache())

    def _updateProviderType(self):
        isSimplified = g_settingsCore.getSetting(settings_constants.GAME.SIMPLIFIED_TTC)
        if isSimplified:
            alias = HANGAR_ALIASES.VEH_PARAMS_RENDERER_UI
        else:
            alias = HANGAR_ALIASES.VEH_PARAMS_RENDERER_BASE_UI
        self.as_setRendererLnkS(alias)
        self._vehParamsDP.setIsSimplified(isSimplified)

    def _getVehicleCache(self):
        return g_currentVehicle

    def __onSettingsChange(self, diff):
        if settings_constants.GAME.SIMPLIFIED_TTC in diff:
            self.changeVehParamsType()


class VehiclePreviewParameters(VehicleParameters):

    def __init__(self):
        super(VehiclePreviewParameters, self).__init__()
        self._paramsProviderCls = _VehPreviewParamsDataProvider

    def _populate(self):
        super(VehiclePreviewParameters, self)._populate()
        g_currentPreviewVehicle.onComponentInstalled += self.update
        g_currentPreviewVehicle.onChanged += self.update

    def _dispose(self):
        g_currentPreviewVehicle.onComponentInstalled -= self.update
        g_currentPreviewVehicle.onChanged -= self.update
        super(VehiclePreviewParameters, self)._dispose()

    def _getVehicleCache(self):
        return g_currentPreviewVehicle


class _VehParamsDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(_VehParamsDataProvider, self).__init__()
        self._list = []
        self._useAnim = False
        self._cache = None
        self._expandedGroups = {}
        self._isSimplified = True
        self._tooltipType = TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS
        return

    def setGroupsToShow(self, groups):
        self._expandedGroups = groups

    def setIsSimplified(self, isSimplified):
        self._isSimplified = isSimplified

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def fini(self):
        self.clear()
        self._dispose()

    def setUseAnim(self, useAnim):
        self._useAnim = useAnim

    @property
    def useAnim(self):
        return self._useAnim

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def refreshItem(self, cache):
        self.buildList(cache)
        return False

    def refreshRandomItems(self, indexes, items):
        self.flashObject.invalidateItems(indexes, items)

    def refreshSingleItem(self, index, item):
        self.flashObject.invalidateItem(index, item)

    def buildList(self, cache):
        self.clear()
        self._cache = cache
        if self._cache.isPresent():
            if self._isSimplified:
                self._buildSimplifiedList()
            else:
                self.__buildBaseList()

    def _getComparator(self):
        return params_helper.idealCrewComparator(self._cache.item)

    def _getSimplifiedValue(self, param):
        return formatters.colorizedFormatParameter(param, formatters.NO_BONUS_SIMPLIFIED_FORMATTERS)

    def _getBaseFormatters(self):
        return formatters.NO_BONUS_BASE_FORMATTERS

    def _buildSimplifiedList(self):
        comparator = self._getComparator()
        stockParams = params_helper.getParameters(g_itemsCache.items.getStockVehicle(self._cache.item.intCD))
        for groupIdx, groupName in enumerate(RELATIVE_PARAMS):
            hasParams = False
            relativeParam = comparator.getExtendedData(groupName)
            self._list.extend([self._makeSimpleParamHeaderVO(relativeParam, self._expandedGroups[groupName]), self._makeSimpleParamBottomVO(relativeParam, stockParams[groupName])])
            if self._expandedGroups[groupName]:
                for paramName in PARAMS_GROUPS[groupName]:
                    param = comparator.getExtendedData(paramName)
                    if param.value is not None:
                        self._list.append(self.__makeAdvancedParamVO(param))
                        hasParams = True

            if hasParams and groupIdx < len(RELATIVE_PARAMS) - 1:
                self._list.append(self.__makeSeparator())

        return

    def __buildBaseList(self):
        parameters = params_helper.getParameters(self._cache.item)
        if parameters is not None:
            formattedParameters = formatters.getFormattedParamsList(self._cache.item.descriptor, parameters)
            for paramName, value in formattedParameters:
                if not formatters.isRelativeParameter(paramName):
                    self._list.append({'titleText': formatters.formatVehicleParamName(paramName),
                     'valueText': text_styles.stats(value),
                     'isEnabled': False})

        return

    def _makeSimpleParamHeaderVO(self, param, isOpen):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_TOP,
         'titleText': formatters.formatVehicleParamName(param.name),
         'valueText': self._getSimplifiedValue(param),
         'paramID': param.name,
         'isEnabled': True,
         'tooltip': self._tooltipType,
         'isOpen': isOpen,
         'showDecreaseArrow': self._showDecreaseArrow(param)}

    def _showDecreaseArrow(self, param):
        return param.state[0] == PARAM_STATE.WORSE

    def _makeSimpleParamBottomVO(self, param, stockValue):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_BOTTOM,
         'paramID': param.name,
         'isEnabled': True,
         'tooltip': self._tooltipType,
         'indicatorVO': {'value': param.value,
                         'maxValue': MAX_RELATIVE_VALUE,
                         'markerValue': stockValue,
                         'minValue': 0,
                         'useAnim': self._useAnim}}

    def __makeAdvancedParamVO(self, param):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_ADVANCED,
         'titleText': formatters.formatVehicleParamName(param.name, False),
         'valueText': formatters.colorizedFormatParameter(param, self._getBaseFormatters()),
         'iconSource': formatters.getParameterIconPath(param.name),
         'paramID': param.name,
         'isEnabled': False,
         'tooltip': self._tooltipType}

    def __makeSeparator(self):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SEPARATOR,
         'isEnabled': False,
         'tooltip': ''}


class _VehPreviewParamsDataProvider(_VehParamsDataProvider):

    def __init__(self):
        super(_VehPreviewParamsDataProvider, self).__init__()
        self._tooltipType = TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_PARAMETERS

    def _getComparator(self):
        return params_helper.vehiclesComparator(self._cache.item, self._cache.defaultItem)

    def _getSimplifiedValue(self, param):
        return formatters.simlifiedDeltaParameter(param)

    def _getBaseFormatters(self):
        return formatters.BASE_FORMATTERS

    def _makeSimpleParamBottomVO(self, param, stockValue):
        vo = super(_VehPreviewParamsDataProvider, self)._makeSimpleParamBottomVO(param, stockValue)
        delta = param.state[1]
        value = param.value
        if delta > 0:
            value -= delta
        vo['indicatorVO'].update({'value': value,
         'delta': delta})
        return vo

    def _showDecreaseArrow(self, param):
        return False
