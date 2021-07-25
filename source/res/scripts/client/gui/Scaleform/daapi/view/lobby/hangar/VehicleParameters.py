# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/VehicleParameters.py
from typing import TYPE_CHECKING, Dict
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from account_helpers.AccountSettings import AccountSettings
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.VehicleParametersMeta import VehicleParametersMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.VEHICLE_PARAM_CONSTANTS import VEHICLE_PARAM_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import params_helper, formatters
from gui.shared.items_parameters.functions import isSituationalBonus
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.shared.items_parameters.formatters import EXTRACTED_BONUS_SCHEME, SITUATIONAL_BONUS_SCHEME
from gui.shared.items_parameters.params_helper import VehParamsBaseGenerator, getParameters, getCommonParam, SimplifiedBarVO
from helpers.i18n import makeString as _ms
from gui.shared.items_parameters.comparator import PARAM_STATE
from uilogging.detachment.loggers import DynamicGroupLogger
from uilogging.detachment.constants import ACTION
from constants import BonusTypes
if TYPE_CHECKING:
    from gui.shared.items_parameters.comparator import _ParameterInfo, VehiclesComparator

class VehicleParameters(VehicleParametersMeta):
    uiLogger = DynamicGroupLogger()

    def __init__(self):
        super(VehicleParameters, self).__init__()
        self._vehParamsDP = None
        self._alreadyShowed = False
        self._expandedGroups = {'relativePower': AccountSettings.getSettings('relativePower'),
         'relativeArmor': AccountSettings.getSettings('relativeArmor'),
         'relativeMobility': AccountSettings.getSettings('relativeMobility'),
         'relativeVisibility': AccountSettings.getSettings('relativeVisibility'),
         'relativeCamouflage': AccountSettings.getSettings('relativeCamouflage'),
         'relativeSituationalBonuses': AccountSettings.getSettings('relativeSituationalBonuses')}
        return

    def onParamClick(self, paramID):
        isOpened = not self._expandedGroups[paramID]
        self.uiLogger.log(ACTION.USE_TTC_SECTION, ttc_group=paramID, status=isOpened)
        AccountSettings.setSettings(paramID, isOpened)
        self._expandedGroups[paramID] = isOpened
        self._setDPUseAnimAndRebuild(False)

    def onListScroll(self):
        self._setDPUseAnimAndRebuild(False)

    def update(self, disallowRebuild=True):
        self._vehParamsDP.setGroupsToShow(self._expandedGroups)
        self._setDPUseAnimAndRebuild(True, disallowRebuild)

    def rebuildParams(self):
        cache = self._getVehicleCache()
        self._vehParamsDP.rebuildList(cache)
        controlLevelParamVisibility = cache.isPresent()
        self.as_setDetachmentVisibleS(controlLevelParamVisibility)
        if controlLevelParamVisibility:
            param = self._vehParamsDP.getTankControlLevelParam()
            self.as_setDetachmentDataS({'vehicleLevel': formatters.simplifiedDeltaParameter(param, useAbsoluteValue=False, reverse=True),
             'vehicleLevelTooltip': {'isSpecial': True,
                                     'specialAlias': TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS,
                                     'specialArgs': [param.name]},
             'roles': self._makeRolesVO()})

    def _createDataProvider(self):
        return _VehParamsDataProvider(_VehParamsGenerator())

    def _populate(self):
        super(VehicleParameters, self)._populate()
        self._vehParamsDP = self._createDataProvider()
        self._vehParamsDP.setFlashObject(self.as_getDPS())
        self.update(disallowRebuild=False)

    def _dispose(self):
        self._vehParamsDP.fini()
        self._vehParamsDP = None
        self._paramsProviderCls = None
        cache = self._getVehicleCache()
        if cache and cache.item:
            perksController = cache.item.getPerksController()
            if perksController:
                perksController.setVehParams(None)
        self.uiLogger.reset()
        super(VehicleParameters, self)._dispose()
        return

    def _setDPUseAnimAndRebuild(self, useAnim, disallowRebuild=False):
        if self._vehParamsDP.useAnim != useAnim:
            self.as_setIsParamsAnimatedS(useAnim)
        self._vehParamsDP.setUseAnim(useAnim)
        cache = self._getVehicleCache()
        if not cache.item:
            return
        perksController = cache.item.getPerksController()
        if not perksController:
            self.rebuildParams()
        else:
            perksController.setVehParams(self)
            if not perksController.isEnabled():
                if not perksController.recalc(True) and not disallowRebuild:
                    self.rebuildParams()

    def _makeRolesVO(self):
        vehItem = self._getVehicleCache().item
        if vehItem:
            return [ {'iconPath': formatters.getVehicleCrewRoleIconPath(role[0]),
             'tooltipData': {'isSpecial': True,
                             'specialAlias': TOOLTIPS_CONSTANTS.CREW_MEMBER,
                             'specialArgs': [role[0]]}} for role in vehItem.crewRoles ]
        return []

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

    def __init__(self, tooltipType=TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS):
        super(_VehParamsGenerator, self).__init__()
        self._tooltipType = tooltipType
        self.useAnim = False

    def _getBaseFormatters(self):
        return formatters.NO_BONUS_BASE_SCHEME

    def _getSimplifiedValue(self, param):
        return formatters.colorizedFormatParameter(param, formatters.NO_BONUS_SIMPLIFIED_SCHEME)

    def _makeSimpleParamBottomVO(self, param, vehicle=None):
        stockParams = getParameters(vehicle)
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

    def _makeAdvancedParamVO(self, param, showValues=True):
        if not param.value:
            return None
        else:
            data = super(_VehParamsGenerator, self)._makeAdvancedParamVO(param, showValues)
            data.update({'titleText': formatters.formatVehicleParamName(param.name, False),
             'valueText': formatters.colorizedFullFormatParameter(param, self._getBaseFormatters()),
             'iconSource': formatters.getParameterSmallIconPath(param.name),
             'isEnabled': False,
             'hasValue': showValues,
             'tooltip': self._getAdvancedParamTooltip(param)})
            return data

    def _makeTankmanSkillAdvancedParamVO(self, skillName):
        data = super(_VehParamsGenerator, self)._makeTankmanSkillAdvancedParamVO(skillName)
        data.update({'titleText': text_styles.main(backport.text(R.strings.item_types.tankman.skills.dyn(skillName)())),
         'tooltip': TOOLTIPS_CONSTANTS.COMMANDER_PERK_GF,
         'isTooltipWulf': True,
         'paramID': skillName.split('_')[1],
         'iconSource': formatters.getParameterSmallIconPath(skillName)})
        return data

    def _getPerkValueText(self, perkLevel, perkPrevLevel, extraBonuses, isOvercap):
        perkLevelText = str(perkLevel) if perkLevel > extraBonuses else '+{}'.format(perkLevel)
        text = perkLevelText
        if extraBonuses > 0:
            text = text_styles.whiteOrangeTitle(perkLevelText) if isOvercap > 0 else text_styles.blueBoosterTitle(perkLevelText)
        if perkPrevLevel is not None:
            diff = perkLevel - perkPrevLevel
            if diff != 0:
                text = makeHtmlString('html_templates:lobby/detachment', 'PerkAdvancedParam' + ('Positive' if diff > 0 else 'Negative'), {'diff': abs(diff),
                 'value': text})
        return text

    def _makeDetachmentPerkAdvancedParamVO(self, perk, prevPerkLevel=None, extraBonuses=0, isOvercap=False):
        data = super(_VehParamsGenerator, self)._makeDetachmentPerkAdvancedParamVO(perk)
        glowType = VEHICLE_PARAM_CONSTANTS.GLOW_TYPE_NONE
        if extraBonuses > 0:
            glowType = VEHICLE_PARAM_CONSTANTS.GLOW_TYPE_RED if isOvercap else VEHICLE_PARAM_CONSTANTS.GLOW_TYPE_BLUE
        data.update({'titleText': text_styles.main(backport.text(perk.name)),
         'valueText': self._getPerkValueText(perk.perkLevel, prevPerkLevel, extraBonuses, isOvercap),
         'tooltip': TOOLTIPS_CONSTANTS.GF_DETACHMENT_PERK,
         'isTooltipWulf': True,
         'iconSource': backport.image(perk.vehParamsIcon),
         'glowType': glowType})
        return data

    def _makeModuleAdvancedParamVO(self, moduleName, moduleType):
        data = super(_VehParamsGenerator, self)._makeModuleAdvancedParamVO(moduleName, moduleType)
        from gui.shared.gui_items.artefacts import getArtefactName
        tooltipID = TOOLTIPS_CONSTANTS.MODULE_PARAMETER if moduleType == BonusTypes.OPTIONAL_DEVICE else TOOLTIPS_CONSTANTS.EQUIPMENT_PARAMETER
        data.update({'titleText': text_styles.main(_ms(getArtefactName(moduleName))),
         'tooltip': tooltipID,
         'iconSource': formatters.getParameterSmallIconPath(moduleName)})
        return data

    def _isExtraParamEnabled(self):
        return True

    def _shouldShowValues(self, vehIntCD):
        vehicle = self.itemsCache.items.getStockVehicle(vehIntCD)
        return not vehicle.isObserver if vehicle else True

    def _makeExtraParamVO(self, param, passiveValue=0.0):
        if not param.value:
            return (None, 0)
        else:
            data, _ = super(_VehParamsGenerator, self)._makeExtraParamVO(param, passiveValue)
            reverted = param.state[0] == PARAM_STATE.WORSE
            if reverted:
                defaultTitleAccessor = R.strings.tank_setup.kpi.bonus.reverted.dyn(param.name)
                title = backport.text(R.strings.tank_setup.kpi.bonus.ttc.reverted.dyn(param.name, defaultTitleAccessor)())
            else:
                defaultTitleAccessor = R.strings.tank_setup.kpi.bonus.dyn(param.name)
                title = backport.text(R.strings.tank_setup.kpi.bonus.ttc.dyn(param.name, defaultTitleAccessor)())
            hasPassiveBonus = any((not isSituationalBonus(bnsId, bnsType, param.name) for bnsId, bnsType in param.bonuses))
            colorScheme = EXTRACTED_BONUS_SCHEME if hasPassiveBonus and passiveValue != 0.0 else SITUATIONAL_BONUS_SCHEME
            data.update({'titleText': text_styles.leadingText(text_styles.main(title), 2),
             'valueText': formatters.colorizedFullFormatParameter(param, colorScheme),
             'isEnabled': False,
             'tooltip': self._getAdvancedParamTooltip(param),
             'iconSource': formatters.getParameterSmallIconPath(param.name)})
            return (data, title.count('\n'))

    def _makeSimpleParamHeaderVO(self, param, isOpen, comparator, showValues=True):
        data = super(_VehParamsGenerator, self)._makeSimpleParamHeaderVO(param, isOpen, comparator, showValues)
        data.update({'titleText': formatters.formatVehicleParamName(param.name),
         'valueText': self._getSimplifiedValue(param) if showValues else '',
         'isEnabled': True,
         'tooltip': self._tooltipType,
         'isOpen': isOpen,
         'buffIconSrc': formatters.getGroupPenaltyIcon(param, comparator)})
        return data

    def _makeSeparator(self):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SEPARATOR,
         'isEnabled': False,
         'tooltip': ''}

    def _makeExtraAdditionalBlock(self, paramID, tooltip):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SEPARATOR,
         'isEnabled': False,
         'tooltip': tooltip,
         'paramID': paramID}

    def _makeLineSeparator(self):
        return {'state': HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_LINE_SEPARATOR,
         'isEnabled': False,
         'tooltip': ''}


class _PreviewVehParamsGenerator(_VehParamsGenerator):

    def __init__(self, tooltipType=None):
        super(_PreviewVehParamsGenerator, self).__init__(tooltipType or TOOLTIPS_CONSTANTS.VEHICLE_PREVIEW_ADVANCED_PARAMETERS)

    def _getSimplifiedValue(self, param):
        return formatters.simplifiedDeltaParameter(param)

    def _getBaseFormatters(self):
        return formatters.BASE_SCHEME

    def _makeSimpleParamBottomVO(self, param, vehicle=None):
        vo = super(_PreviewVehParamsGenerator, self)._makeSimpleParamBottomVO(param, vehicle)
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

    def getTankControlLevelParam(self):
        comparator = self._getComparator()
        return comparator.getExtendedData('relativeTankControlLevel')

    def _getSimplifiedValue(self, param):
        return formatters.colorizedFormatParameter(param, formatters.NO_BONUS_SIMPLIFIED_SCHEME)

    def _buildSimplifiedList(self):
        self._list = self._paramsGenerator.getFormattedParams(self._getComparator(), self._expandedGroups, self._cache.item.intCD)


class VehPreviewParamsDataProvider(_VehParamsDataProvider):

    def __init__(self, tooltipType=None):
        super(VehPreviewParamsDataProvider, self).__init__(_PreviewVehParamsGenerator(tooltipType))

    def _getComparator(self):
        return params_helper.vehiclesComparator(self._cache.item, self._cache.defaultItem, bonuses=True)


class TankSetupParamsDataProvider(VehPreviewParamsDataProvider):

    def _getComparator(self):
        return params_helper.tankSetupVehiclesComparator(self._cache.item, self._cache.defaultItem)
