# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/sub_views/vehicle_params_view.py
from __future__ import absolute_import, division
import json
from future.utils import iteritems
from account_helpers import AccountSettings
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_param_base_view_model import HighlightType
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_param_group_view_model import VehicleParamGroupViewModel
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_param_view_model import VehicleParamViewModel
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_params_view_model import VehicleParamsViewModel
from gui.impl.lobby.hangar.sub_views.veh_param_helpers import getGroupIcon, formatParameterValue, formatAdditionalParameter, getMaxValue
from gui.impl.pub.view_component import ViewComponent
from gui.shared.gui_items import KPI, VEHICLE_ATTR_TO_KPI_NAME_MAP, GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.items_parameters import RELATIVE_PARAMS, params_helper
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.param_name_helper import getVehicleParameterText
from gui.shared.items_parameters.params import HIDDEN_PARAM_DEFAULTS
from gui.shared.items_parameters.params_helper import hasSituationalEffect
from gui.shared.tooltips.contexts import HangarParamContext
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IIGRController
from skeletons.gui.shared import IItemsCache
_HIGHLIGHT_TYPE_STATE_MAP = {PARAM_STATE.BETTER: HighlightType.INCREASE,
 PARAM_STATE.WORSE: HighlightType.DECREASE,
 PARAM_STATE.SITUATIONAL: HighlightType.SITUATIONAL}

class _VehicleParamsPresenterBase(ViewComponent[VehicleParamsViewModel]):
    _DEFAULT_MIN_VALUE = 0
    _N_DIGITS = 2
    __igrController = dependency.descriptor(IIGRController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID=R.views.lobby.hangar.subViews.VehicleParams(), applyFormatting=True):
        self.__context = HangarParamContext()
        self.__params = []
        self.__extraParams = []
        self.__expandedGroups = None
        self.__comparator = None
        self.__stockParams = None
        self._applyFormatting = applyFormatting
        super(_VehicleParamsPresenterBase, self).__init__(layoutID, VehicleParamsViewModel)
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if tooltipId in self._getParamTooltips():
                paramId = event.getArgument('paramId', None)
                toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
                if toolTipMgr is not None:
                    toolTipMgr.onCreateWulfTooltip(tooltipId, (paramId, self.__context, True), event.mouse.positionX, event.mouse.positionY)
                    return tooltipId
        return super(_VehicleParamsPresenterBase, self).createToolTip(event)

    @property
    def comparator(self):
        if self.__comparator is None:
            self.__comparator = self._getComparator()
        return self.__comparator

    @property
    def viewModel(self):
        return super(_VehicleParamsPresenterBase, self).getViewModel()

    @property
    def groups(self):
        return self.__groups

    @property
    def params(self):
        return self.__params

    @property
    def extraParams(self):
        return self.__extraParams

    @property
    def expandedGroups(self):
        return self.__expandedGroups if self.__expandedGroups is not None else {'relativePower': AccountSettings.getSettings('relativePower'),
         'relativeArmor': AccountSettings.getSettings('relativeArmor'),
         'relativeMobility': AccountSettings.getSettings('relativeMobility'),
         'relativeVisibility': AccountSettings.getSettings('relativeVisibility'),
         'relativeCamouflage': AccountSettings.getSettings('relativeCamouflage')}

    def setExpandedGroups(self, value):
        self.__expandedGroups = value

    def updateModel(self):
        if not GUI_SETTINGS.technicalInfo:
            return
        self._clearData()
        self._prepareData()
        self.__fillViewModel()

    def setContext(self, context):
        self.__context = context

    def _getContext(self):
        return self.__context

    def _getComparator(self):
        return params_helper.similarCrewComparator(self._getVehicle())

    def _getVehicle(self):
        raise NotImplementedError

    def _getDefaultVehicle(self):
        return self._getVehicle()

    def _onLoading(self, *args, **kwargs):
        super(_VehicleParamsPresenterBase, self)._onLoading(*args, **kwargs)
        self.updateModel()

    def _getEvents(self):
        return ((self.__igrController.onIgrTypeChanged, self._onIgrTypeChanged), (self.__itemsCache.onSyncCompleted, self._onCacheResync), (self.viewModel.onGroupClick, self.__onGroupClick))

    def _finalize(self):
        super(_VehicleParamsPresenterBase, self)._finalize()
        self.__context = None
        self.__params = None
        self.__extraParams = None
        self.__expandedGroups = None
        self.__comparator = None
        self.__stockParams = None
        return

    def _onIgrTypeChanged(self):
        self.__fillViewModel()

    def _onCacheResync(self, reason, diff):
        if reason in (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            vehicle = self._getVehicle()
            if vehicle is not None and any((vehicle.intCD in diff.get(itemType, {}) for itemType in (GUI_ITEM_TYPE.VEH_POST_PROGRESSION, GUI_ITEM_TYPE.VEHICLE))):
                self.updateModel()
        return

    @property
    def _stockParams(self):
        if self.__stockParams is None:
            self._updateStockParams()
        return self.__stockParams

    def _updateStockParams(self):
        self.__stockParams = params_helper.getParameters(self.__itemsCache.items.getStockVehicle(self._getDefaultVehicle().intCD))

    def _clearData(self):
        self.__groups = []
        self.__params = []
        self.__extraParams = []
        self.__comparator = None
        return

    def _getGroupHighlight(self, _):
        return HighlightType.NONE

    def _getGroupEnabled(self, _):
        return True

    def _getUseAnim(self):
        return True

    def _getParamEnabled(self, *_):
        return True

    def _getRoundNDigits(self):
        return self._N_DIGITS

    def _getTooltipID(self):
        return TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS

    def _getAdvancedParamTooltip(self):
        return TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS

    def _getParamTooltips(self):
        return {self._getTooltipID(), self._getAdvancedParamTooltip()}

    def _isExtraParamEnabled(self):
        return False

    def _isAdditionalValueEnabled(self):
        return False

    def _isAdditionalValueApproximately(self):
        return False

    def _getLocalizedName(self, param, applyFormatting=True):
        if applyFormatting:
            if KPI.Name.hasValue(param.name):
                isPositive = param.value >= 0
                paramName = VEHICLE_ATTR_TO_KPI_NAME_MAP.get(param.name, param.name)
                name = getVehicleParameterText(paramName, isPositive=isPositive, isTTC=True)
            else:
                name = R.strings.menu.tank_params.dyn(param.name)()
            return backport.text(name)
        if KPI.Name.hasValue(param.name):
            key = 'positive' if param.value >= 0 else 'negative'
            name = VEHICLE_ATTR_TO_KPI_NAME_MAP.get(param.name, param.name)
            return json.dumps({'key': key,
             'name': name})

    def _createGroupViewModel(self, groupName, comparator):
        param = comparator.getExtendedData(groupName)
        additionalValue = formatAdditionalParameter(param, isApproximately=self._isAdditionalValueApproximately())
        return {'Id': groupName,
         'IsEnabled': self._getGroupEnabled(groupName),
         'Value': formatParameterValue(param.name, param.value, param.state, allowSmartRound=False, isColorize=False, nDigits=self._getRoundNDigits()),
         'HighlightType': self._getGroupHighlight(groupName),
         'IsSituational': hasSituationalEffect(param.name, self.comparator),
         'TooltipID': self._getTooltipID(),
         'BuffIconType': getGroupIcon(param, self.comparator),
         'IsOpen': self._getIsOpened(groupName=groupName),
         'AdditionalValue': additionalValue if self._isAdditionalValueEnabled() else '',
         'Indicator': self._createIndicator(param)}

    def _createIndicator(self, param):
        state, delta = param.state
        if state == PARAM_STATE.WORSE:
            delta = -abs(delta)
        maxValue = getMaxValue(param.value, delta)
        return {'Value': param.value,
         'Delta': delta,
         'MarkerValue': self._stockParams[param.name],
         'MaxValue': maxValue,
         'MinValue': self._DEFAULT_MIN_VALUE,
         'IsUseAnim': self._getUseAnim(),
         'ModifiedPercent': int(param.value * 100 / (maxValue - self._DEFAULT_MIN_VALUE)),
         'CurrentPercent': int(self._stockParams[param.name] * 100 / (maxValue - self._DEFAULT_MIN_VALUE))}

    def _createParam(self, param, groupName, highlight=HighlightType.NONE):
        return None if param.value is None else {'Id': param.name,
         'ParentID': groupName,
         'HighlightType': highlight,
         'IsEnabled': self._getParamEnabled(param, groupName),
         'Value': formatParameterValue(param.name, param.value, self._applyFormatting, param.state, allowSmartRound=False, nDigits=self._getRoundNDigits()),
         'TooltipID': self._getAdvancedParamTooltip(),
         'Name': self._getLocalizedName(param, self._applyFormatting)}

    def _prepareData(self, diffParams=None, concreteGroup=None):
        if self._getVehicle() is None:
            return
        else:
            diffParams = diffParams if diffParams is not None else {}
            for _, groupName in enumerate(RELATIVE_PARAMS):
                if concreteGroup is not None and concreteGroup != groupName:
                    continue
                group = self._createGroupViewModel(groupName=groupName, comparator=self.comparator)
                self.__groups.append(group)
                if not self._getIsOpened(groupName):
                    continue
                for paramName in params_helper.PARAMS_GROUPS[groupName]:
                    self.__addParam(paramName, groupName, diffParams, self.__params)

                if self._isExtraParamEnabled():
                    for paramName in params_helper.EXTRA_PARAMS_GROUP[groupName]:
                        self.__addParam(paramName, groupName, diffParams, self.__extraParams, skipMissing=True)

            return

    def __addParam(self, paramName, groupName, diffParams, paramsContainer, skipMissing=False):
        param = self.comparator.getExtendedData(paramName)
        if skipMissing and (not param.value or paramName in HIDDEN_PARAM_DEFAULTS and param.value == HIDDEN_PARAM_DEFAULTS[paramName]):
            return
        if param.mustHighlight:
            highlight = HighlightType.INCREASE if not param.isSituational else HighlightType.SITUATIONAL
        else:
            highlight = self.__getHighlightType(paramName, diffParams, param.state)
        paramModel = self._createParam(param, groupName, highlight)
        if paramModel:
            paramsContainer.append(paramModel)

    def __getHighlightType(self, paramName, diffParams, paramState):
        if diffParams:
            return diffParams.get(paramName, HighlightType.NONE)
        elif paramState is None:
            return HighlightType.NONE
        else:
            if isinstance(paramState[0], (tuple, list)):
                stateType, _ = paramState[0]
            else:
                stateType = paramState[0]
            return _HIGHLIGHT_TYPE_STATE_MAP.get(stateType, HighlightType.NONE)

    def _getIsOpened(self, groupName):
        return self.expandedGroups is None or self.expandedGroups.get(groupName, False)

    def __fillViewModel(self):
        if self._getVehicle() is None:
            return
        else:
            with self.viewModel.transaction() as model:
                groups = model.getGroups()
                groups.clear()
                for group in self.__groups:
                    groupID = group.get('Id', '')
                    groupModel = self.__convertGroupToModel(group)
                    params = groupModel.getParams()
                    params.clear()
                    extraParams = groupModel.getExtraParams()
                    extraParams.clear()
                    for param in self.__params:
                        paramID = param.get('ParentID', '')
                        if paramID == groupID:
                            params.addViewModel(self.__fillModel(VehicleParamViewModel(), param))

                    for extraParam in self.__extraParams:
                        paramID = extraParam.get('ParentID', '')
                        if paramID == groupID:
                            extraParams.addViewModel(self.__fillModel(VehicleParamViewModel(), extraParam))

                    groups.addViewModel(groupModel)

                groups.invalidate()
            return

    def __fillModel(self, model, params):
        for k, v in iteritems(params):
            modelSetter = 'set' + k
            if hasattr(model, modelSetter):
                getattr(model, modelSetter)(v)

        return model

    def __convertGroupToModel(self, item):
        groupModel = self.__fillModel(VehicleParamGroupViewModel(), item)
        indicator = item.get('Indicator', None)
        if indicator is not None:
            self.__fillModel(groupModel.indicator, indicator)
        return groupModel

    def __onGroupClick(self, args=None):
        if not args:
            return
        else:
            groupName = args.get('groupName', None)
            if groupName:
                for group in self.viewModel.getGroups():
                    if groupName == group.getId():
                        isOpened = not group.getIsOpen()
                        group.setIsOpen(isOpened)
                        AccountSettings.setSettings(groupName, isOpened)

            self.viewModel.getGroups().invalidate()
            self.updateModel()
            return


class CurrentVehicleParamsPresenter(_VehicleParamsPresenterBase):

    def _getEvents(self):
        from CurrentVehicle import g_currentVehicle
        return super(CurrentVehicleParamsPresenter, self)._getEvents() + ((g_currentVehicle.onChanged, self.__onCurrentVehicleChanged),)

    def _getVehicle(self):
        from CurrentVehicle import g_currentVehicle
        return g_currentVehicle.item

    def __onCurrentVehicleChanged(self):
        from CurrentVehicle import g_currentVehicle
        if g_currentVehicle.isPresent():
            self._updateStockParams()
            self.updateModel()


class PreviewVehicleParamsPresenter(_VehicleParamsPresenterBase):

    def _getEvents(self):
        from CurrentVehicle import g_currentPreviewVehicle
        return super(PreviewVehicleParamsPresenter, self)._getEvents() + (g_currentPreviewVehicle.onChanged, self.__onPreviewVehicleChanged)

    def _getComparator(self):
        return params_helper.previewVehiclesComparator(self._getVehicle(), self._getVehicle())

    def _getVehicle(self):
        from CurrentVehicle import g_currentPreviewVehicle
        return g_currentPreviewVehicle.item

    def __onPreviewVehicleChanged(self):
        from CurrentVehicle import g_currentPreviewVehicle
        if g_currentPreviewVehicle.isPresent():
            self._updateStockParams()
            self.updateModel()


class VehicleParamsPresenter(_VehicleParamsPresenterBase):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehIntCD, layoutID=R.views.lobby.hangar.subViews.VehicleParams(), applyFormatting=True):
        super(VehicleParamsPresenter, self).__init__(layoutID=layoutID, applyFormatting=applyFormatting)
        self.__vehIntCD = vehIntCD

    def setVehicle(self, vehIntCD):
        if self.__vehIntCD != vehIntCD:
            self.__vehIntCD = vehIntCD
            self.__comparator = self._getComparator()
            self._updateStockParams()
            self.updateModel()

    def _getVehicle(self):
        return self.__itemsCache.items.getItemByCD(self.__vehIntCD)


class VehicleCompareParamsPresenter(_VehicleParamsPresenterBase):
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, baseVehicle, changedVehicle, *args, **kwargs):
        self._baseVehicle = baseVehicle
        self._changedVehicle = changedVehicle
        super(VehicleCompareParamsPresenter, self).__init__(*args, **kwargs)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            paramId = event.getArgument('paramId', None)
            tooltipId = self._getGroupTooltipID() if paramId in self.expandedGroups else self._getTooltipID()
            toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
            if toolTipMgr is not None:
                toolTipMgr.onCreateWulfTooltip(tooltipId, (paramId, self._getContext(), True), event.mouse.positionX, event.mouse.positionY)
                return tooltipId
        return super(VehicleCompareParamsPresenter, self).createToolTip(event)

    def _getComparator(self):
        return params_helper.previewVehiclesComparator(self._getChangedVehicle(), self._getVehicle(), withSituational=True)

    def _getVehicle(self):
        return self._baseVehicle

    def _finalize(self):
        self._baseVehicle = None
        self._changedVehicle = None
        super(VehicleCompareParamsPresenter, self)._finalize()
        return

    def _onIgrTypeChanged(self):
        pass

    def _onCurrentVehicleChanged(self):
        pass

    def _onCacheResync(self, *_):
        pass

    def _getTooltipID(self):
        return TOOLTIPS_CONSTANTS.BASE_VEHICLE_PARAMETERS

    def _getGroupTooltipID(self):
        return TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS

    def _getAdvancedParamTooltip(self):
        return TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS

    def _getChangedVehicle(self):
        return self._changedVehicle

    def _isExtraParamEnabled(self):
        return True

    def _isAdditionalValueEnabled(self):
        return True


class VehicleSkillPreviewParamsPresenter(CurrentVehicleParamsPresenter):

    def __init__(self):
        super(VehicleSkillPreviewParamsPresenter, self).__init__()
        self.__skillName = ''
        self.__highlightedSkills = ''

    def updateForSkill(self, skillName, highlightedSkills=None):
        self.__skillName = skillName
        self.__highlightedSkills = highlightedSkills
        self.updateModel()

    def _getComparator(self):
        return params_helper.skillOnSimilarCrewComparator(self._getVehicle(), self.__skillName, self.__highlightedSkills)

    def _isExtraParamEnabled(self):
        return True

    def _isAdditionalValueEnabled(self):
        return True


class EasyTankEquipParamsPresenter(_VehicleParamsPresenterBase):

    def __init__(self, vehicle, changedVehicle):
        super(EasyTankEquipParamsPresenter, self).__init__()
        self._vehicle = vehicle
        self._changedVehicle = changedVehicle

    def _getTooltipID(self):
        return TOOLTIPS_CONSTANTS.EASY_TANK_EQUIP_VEHICLE_ADVANCED_PARAMETERS

    def _getAdvancedParamTooltip(self):
        return TOOLTIPS_CONSTANTS.EASY_TANK_EQUIP_VEHICLE_ADVANCED_PARAMETERS

    def _finalize(self):
        self._vehicle = None
        self._changedVehicle = None
        super(EasyTankEquipParamsPresenter, self)._finalize()
        return

    def _onCacheResync(self, *_):
        pass

    def _onIgrTypeChanged(self):
        pass

    def _isExtraParamEnabled(self):
        return True

    def _isAdditionalValueEnabled(self):
        return True

    def _getVehicle(self):
        return self._vehicle

    def _getChangedVehicle(self):
        return self._changedVehicle

    def _getComparator(self):
        return params_helper.previewVehiclesComparator(self._getChangedVehicle(), self._getVehicle(), withSituational=True)
