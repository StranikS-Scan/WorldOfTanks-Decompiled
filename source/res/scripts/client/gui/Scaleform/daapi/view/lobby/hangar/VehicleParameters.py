# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/VehicleParameters.py
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view.meta.VehicleParametersMeta import VehicleParametersMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.items_parameters import params_helper, formatters
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.shared.items_parameters.params_helper import VehParamsBaseGenerator, getParameters, getCommonParam, SimplifiedBarVO
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.items_parameters.comparator import PARAM_STATE

class VehicleParameters(VehicleParametersMeta):

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

    def onParamClick(self, paramID):
        isOpened = not self._expandedGroups[paramID]
        AccountSettings.setSettings(paramID, isOpened)
        self._expandedGroups[paramID] = isOpened
        self._setDPUseAnimAndRebuild(False)

    def onListScroll(self):
        self._setDPUseAnimAndRebuild(False)

    def update(self, *_):
        self._vehParamsDP.setGroupsToShow(self._expandedGroups)
        self._setDPUseAnimAndRebuild(True)

    def _createDataProvider(self):
        return _VehParamsDataProvider(_VehParamsGenerator())

    def _populate(self):
        super(VehicleParameters, self)._populate()
        self._vehParamsDP = self._createDataProvider()
        self._vehParamsDP.setFlashObject(self.as_getDPS())
        self.update()

    def _dispose(self):
        self._vehParamsDP.fini()
        self._vehParamsDP = None
        self._paramsProviderCls = None
        super(VehicleParameters, self)._dispose()
        return

    def _setDPUseAnimAndRebuild(self, useAnim):
        if self._vehParamsDP.useAnim != useAnim:
            self.as_setIsParamsAnimatedS(useAnim)
        self._vehParamsDP.setUseAnim(useAnim)
        self._vehParamsDP.rebuildList(self._getVehicleCache())

    def _getVehicleCache(self):
        return g_currentVehicle


class VehiclePreviewParameters(VehicleParameters):

    def _createDataProvider(self):
        return VehPreviewParamsDataProvider()

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
    _AVERAGE_PARAMS = ('avgDamage', 'avgPiercingPower')
    _AVERAGE_TOOLTIPS_MAP = {TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS: TOOLTIPS_CONSTANTS.VEHICLE_AVG_PARAMETERS,
     TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_ADVANCED_PARAMETERS: TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_AVG_PARAMETERS}
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tooltipType=TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS):
        super(_VehParamsGenerator, self).__init__()
        self._tooltipType = tooltipType
        self.useAnim = False

    def _getBaseFormatters(self):
        return formatters.NO_BONUS_BASE_SCHEME

    def _getSimplifiedValue(self, param):
        return formatters.colorizedFormatParameter(param, formatters.NO_BONUS_SIMPLIFIED_SCHEME)

    def _makeSimpleParamBottomVO(self, param, vehIntCD=None):
        stockParams = getParameters(self.itemsCache.items.getStockVehicle(vehIntCD))
        data = getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_BOTTOM, param.name)
        delta = 0
        state, diff = param.state
        if state == PARAM_STATE.WORSE:
            delta = -abs(diff)
        data.update({'isEnabled': True,
         'tooltip': self._tooltipType,
         'indicatorVO': SimplifiedBarVO(value=param.value, delta=delta, markerValue=stockParams[param.name], useAnim=self.useAnim)})
        return data

    def _getAdvancedParamTooltip(self, param):
        return self._AVERAGE_TOOLTIPS_MAP[self._tooltipType] if param.name in self._AVERAGE_PARAMS and self._tooltipType in self._AVERAGE_TOOLTIPS_MAP else self._tooltipType

    def _makeAdvancedParamVO(self, param):
        if param.value:
            data = super(_VehParamsGenerator, self)._makeAdvancedParamVO(param)
            data.update({'titleText': formatters.formatVehicleParamName(param.name, False),
             'valueText': formatters.colorizedFullFormatParameter(param, self._getBaseFormatters()),
             'iconSource': formatters.getParameterSmallIconPath(param.name),
             'isEnabled': False,
             'tooltip': self._getAdvancedParamTooltip(param)})
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
         'buffIconSrc': formatters.getGroupPenaltyIcon(param, comparator)})
        return data

    def _makeSeparator(self):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SEPARATOR,
         'isEnabled': False,
         'tooltip': ''}


class _PreviewVehParamsGenerator(_VehParamsGenerator):

    def __init__(self, tooltipType=None):
        super(_PreviewVehParamsGenerator, self).__init__(tooltipType or TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_ADVANCED_PARAMETERS)

    def _getSimplifiedValue(self, param):
        return formatters.simplifiedDeltaParameter(param)

    def _getBaseFormatters(self):
        return formatters.BASE_SCHEME

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
        self._paramsGenerator = paramsGenerator
        return

    def setGroupsToShow(self, groups):
        self._expandedGroups = groups

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []

    def fini(self):
        self.clear()
        self.destroy()

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
            self._buildSimplifiedList()

    def _getComparator(self):
        return params_helper.idealCrewComparator(self._cache.item)

    def _getSimplifiedValue(self, param):
        return formatters.colorizedFormatParameter(param, formatters.NO_BONUS_SIMPLIFIED_SCHEME)

    def _buildSimplifiedList(self):
        self._list = self._paramsGenerator.getFormattedParams(self._getComparator(), self._expandedGroups, self._cache.item.intCD)


class VehPreviewParamsDataProvider(_VehParamsDataProvider):

    def __init__(self, tooltipType=None):
        super(VehPreviewParamsDataProvider, self).__init__(_PreviewVehParamsGenerator(tooltipType))

    def _getComparator(self):
        return params_helper.vehiclesComparator(self._cache.item, self._cache.defaultItem)
