# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/VehicleParameters.py
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core import settings_constants
from gui.Scaleform.daapi.view.meta.VehicleParametersMeta import VehicleParametersMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.items_parameters import params_helper, formatters
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.shared.formatters import text_styles
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.items_parameters.params_helper import VehParamsBaseGenerator, getParameters, getCommonParam, SimplifiedBarVO
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class VehicleParameters(VehicleParametersMeta):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(VehicleParameters, self).__init__()
        self._vehParamsDP = None
        self._alreadyShowed = False
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

    def _createDataProvider(self):
        return _VehParamsDataProvider(_VehParamsGenerator())

    def _populate(self):
        super(VehicleParameters, self)._populate()
        self.settingsCore.onSettingsChanged += self.__onSettingsChange
        self._vehParamsDP = self._createDataProvider()
        self._vehParamsDP.setFlashObject(self.as_getDPS())
        self._updateProviderType()
        self.update()

    def _dispose(self):
        self._vehParamsDP.fini()
        self._vehParamsDP = None
        self._paramsProviderCls = None
        self.settingsCore.onSettingsChanged -= self.__onSettingsChange
        super(VehicleParameters, self)._dispose()
        return

    def _setDPUseAnimAndRebuild(self, useAnim):
        if self._vehParamsDP.useAnim != useAnim:
            self.as_setIsParamsAnimatedS(useAnim)
        self._vehParamsDP.setUseAnim(useAnim)
        self._vehParamsDP.rebuildList(self._getVehicleCache())

    def _updateProviderType(self):
        isSimplified = self.settingsCore.getSetting(settings_constants.GAME.SIMPLIFIED_TTC)
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

    def _createDataProvider(self):
        return _VehPreviewParamsDataProvider()

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


class _VehParamsGenerator(VehParamsBaseGenerator):

    def __init__(self, tooltipType=TOOLTIPS_CONSTANTS.VEHICLE_PARAMETERS):
        super(_VehParamsGenerator, self).__init__()
        self._tooltipType = tooltipType
        self.useAnim = False

    def _getBaseFormatters(self):
        return formatters.NO_BONUS_BASE_FORMATTERS

    def _getSimplifiedValue(self, param):
        return formatters.colorizedFormatParameter(param, formatters.NO_BONUS_SIMPLIFIED_FORMATTERS)

    def _makeSimpleParamBottomVO(self, param, vehIntCD=None):
        stockParams = getParameters(g_itemsCache.items.getStockVehicle(vehIntCD))
        data = getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_BOTTOM, param.name)
        data.update({'isEnabled': True,
         'tooltip': self._tooltipType,
         'indicatorVO': SimplifiedBarVO(value=param.value, markerValue=stockParams[param.name], useAnim=self.useAnim)})
        return data

    def _makeAdvancedParamVO(self, param):
        if param.value:
            data = super(_VehParamsGenerator, self)._makeAdvancedParamVO(param)
            data.update({'titleText': formatters.formatVehicleParamName(param.name, False),
             'valueText': formatters.colorizedFormatParameter(param, self._getBaseFormatters()),
             'iconSource': formatters.getParameterIconPath(param.name),
             'isEnabled': False,
             'tooltip': self._tooltipType})
            return data
        else:
            return None

    def _makeSimpleParamHeaderVO(self, param, isOpen, comparator):
        data = super(_VehParamsGenerator, self)._makeSimpleParamHeaderVO(param, isOpen, comparator)
        data.update({'titleText': formatters.formatVehicleParamName(param.name),
         'valueText': self._getSimplifiedValue(param),
         'isEnabled': True,
         'tooltip': self._tooltipType,
         'isOpen': isOpen,
         'buffIconSrc': params_helper.getBuffIcon(param, comparator)})
        return data

    def _makeSeparator(self):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SEPARATOR,
         'isEnabled': False,
         'tooltip': ''}


class _PreviewVehParamsGenerator(_VehParamsGenerator):

    def __init__(self):
        super(_PreviewVehParamsGenerator, self).__init__(TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_PARAMETERS)

    def _getSimplifiedValue(self, param):
        return formatters.simlifiedDeltaParameter(param)

    def _getBaseFormatters(self):
        return formatters.BASE_FORMATTERS

    def _makeSimpleParamBottomVO(self, param, vehIntCD=None):
        vo = super(_PreviewVehParamsGenerator, self)._makeSimpleParamBottomVO(param, vehIntCD)
        delta = param.state[1]
        value = param.value
        if delta > 0:
            value -= delta
        vo['indicatorVO'].update({'value': value,
         'delta': delta})
        return vo


class _VehParamsDataProvider(SortableDAAPIDataProvider):

    def __init__(self, paramsGenerator):
        super(_VehParamsDataProvider, self).__init__()
        self._list = []
        self._useAnim = False
        self._cache = None
        self._expandedGroups = {}
        self._isSimplified = True
        self._paramsGenerator = paramsGenerator
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
        self._paramsGenerator.useAnim = useAnim

    @property
    def useAnim(self):
        return self._paramsGenerator.useAnim

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

    def _buildSimplifiedList(self):
        self._list = self._paramsGenerator.getFormattedParams(self._getComparator(), self._expandedGroups, self._cache.item.intCD)

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


class _VehPreviewParamsDataProvider(_VehParamsDataProvider):

    def __init__(self):
        super(_VehPreviewParamsDataProvider, self).__init__(_PreviewVehParamsGenerator())

    def _getComparator(self):
        return params_helper.vehiclesComparator(self._cache.item, self._cache.defaultItem)
