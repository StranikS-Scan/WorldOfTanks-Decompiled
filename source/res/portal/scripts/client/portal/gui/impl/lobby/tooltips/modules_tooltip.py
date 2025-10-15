# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/modules_tooltip.py
from frameworks.wulf import ViewSettings
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters.comparator import PARAM_STATE
from portal.gui.impl.gen.view_models.views.lobby.tooltips.modules_parameters import ModulesParameters
from portal.gui.impl.gen.view_models.views.lobby.params_ttx_model import TtxComparisonStatus
from portal.gui.impl.gen.view_models.views.lobby.tooltips.modules_tooltip_model import ModulesTooltipModel
from portal.gui.impl.gen.view_models.views.lobby.node_stage_model import ItemType, ItemModifier
from portal.gui.impl.gen.view_models.views.lobby.tooltips.parameters_values import ParametersValues
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from frameworks.wulf import Array
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController
from portal_common.portal_account_helpers.vehicle_upgrade_tree import MAX_NODES_PER_LEVEL
from gui.shared.items_parameters import params_helper, formatters
from helpers import i18n
from gui.impl import backport
from skeletons.gui.shared import IItemsCache
from portal.vehicle_helpers.portal_params_helper import PortalParamsHelper
from gui.shared.gui_items.Vehicle import Vehicle
from gui.doc_loaders.battle_royale_settings_loader import getBattleRoyaleSettings
from items import getTypeOfCompactDescr, vehicles, ITEM_TYPE_NAMES

class ModulesTooltip(ViewImpl):
    __slots__ = ('__level', '__upgradeNode')
    __portalController = dependency.descriptor(IPortalEventController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __ignoredParams = ('weight', 'circularVisionRadius')

    def __init__(self, itemId):
        settings = ViewSettings(R.views.portal.lobby.tooltips.ModulesTooltip())
        settings.model = ModulesTooltipModel()
        itemId = int(itemId)
        vehicle = self.__portalController.getCurrentSelectedVehicle()
        upgradeNodes = self.__portalController.getVehicleUpgradeNodes(vehicle)
        self.__level = itemId / MAX_NODES_PER_LEVEL
        index = itemId % MAX_NODES_PER_LEVEL
        self.__upgradeNode = upgradeNodes[self.__level]['nodes'][index]
        super(ModulesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ModulesTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ModulesTooltip, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillData(model)

    def __fillData(self, model):
        if self.__upgradeNode['modules']:
            fittingModule = self.__itemsCache.items.getItemByCD(self.__upgradeNode['modules'][0])
            model.setItemType(ItemType(fittingModule.itemTypeName))
            model.setModuleModifier(ItemModifier(self.__upgradeNode['itemModifier']))
            model.setModuleName(fittingModule.userName)
            model.setNextLevel(self.__level + 2)
            self.__fillParameters(model)
            model.setIsModule(True)
        elif self.__upgradeNode['vehicleModifiers']:
            itemType = self.__upgradeNode['itemType']
            model.setItemType(ItemType(itemType))
            model.setNextLevel(self.__level + 2)
            self.__fillBoostParameters(model)
            model.setIsModule(False)

    def __fillBoostParameters(self, model):
        model.bonusParameter.setValue(self.__floatToPercentage(self.__upgradeNode['vehicleModifiers'][0]['modifier']))
        descr = backport.text(R.strings.portal_tooltips.params.desc.dyn(self.__upgradeNode['itemType'])())
        model.bonusParameter.setDescription(descr)

    def __fillParameters(self, model):
        parametersArray = Array()
        currentVehicle = self.__portalController.getCurrentSelectedVehicle()
        vDescr = currentVehicle.descriptor
        fittingModule = self.__itemsCache.items.getItemByCD(self.__upgradeNode['modules'][0])
        currModuleDescr, _ = vDescr.getComponentsByType(fittingModule.itemTypeName)
        currModule = self.__itemsCache.items.getItemByCD(currModuleDescr.compactDescr)
        moduleData = self.__getPortalTreeModuleSettings(fittingModule)
        paramsList = []
        if moduleData is not None:
            paramsList = tuple((param for param in moduleData.params if param not in self.__ignoredParams))
        for paramName in paramsList:
            moduleModel = ModulesParameters()
            comparator = params_helper.itemsComparator(fittingModule, currModule, vDescr)
            paramInfo = comparator.getExtendedData(paramName)
            values, states = self.__getValuesAndStates(paramInfo)
            if values is None or None in values:
                continue
            self.__fillDescrAndMeasurments(moduleModel, paramName, vDescr)
            self.__fillModuleDescription(moduleModel, values, states)
            parametersArray.addViewModel(moduleModel)

        maxHealthDifference = self.__getMaxHealthDifference(currModule, fittingModule, currentVehicle)
        if maxHealthDifference > 0:
            moduleModel = ModulesParameters()
            paramName = 'maxHealth'
            self.__fillDescrAndMeasurments(moduleModel, paramName, vDescr)
            self.__fillModuleDescription(moduleModel, [maxHealthDifference], [(PARAM_STATE.BETTER, '')])
            parametersArray.addViewModel(moduleModel)
        itemTypeID, _, _ = vehicles.parseIntCompactDescr(fittingModule.intCD)
        if ITEM_TYPE_NAMES[itemTypeID] == 'vehicleChassis':
            originalParams = PortalParamsHelper.getVehicleParams(currentVehicle)
            comparedVehicle = Vehicle(strCompactDescr=currentVehicle.strCD)
            comparedDescr = comparedVehicle.descriptor
            comparedDescr.installComponent(fittingModule.intCD)
            comparedParams = PortalParamsHelper.getVehicleParams(comparedVehicle)
            compareResult = PortalParamsHelper.getComparedParams(originalParams, comparedParams)
            hullArmor = next((obj for obj in compareResult if obj.name == 'hullArmor'), None)
            if hullArmor is not None:
                moduleModel = ModulesParameters()
                paramName = hullArmor.name
                self.__fillDescrAndMeasurments(moduleModel, paramName, vDescr)
                armorValues = [ obj.value for obj in hullArmor.values ]
                statusMapping = {TtxComparisonStatus.INCREASE: PARAM_STATE.BETTER,
                 TtxComparisonStatus.DECREASE: PARAM_STATE.WORSE,
                 TtxComparisonStatus.DEFAULT: PARAM_STATE.NORMAL}
                armorStates = [ (statusMapping.get(obj.status, PARAM_STATE.NORMAL), '') for obj in hullArmor.values ]
                self.__fillModuleDescription(moduleModel, armorValues, armorStates)
                parametersArray.addViewModel(moduleModel)
        model.setParameters(parametersArray)
        return

    def __fillDescrAndMeasurments(self, moduleModel, paramName, vDescr):
        titleName = formatters.getTitleParamName(vDescr, paramName)
        measureName = formatters.getMeasureParamName(vDescr, paramName)
        measureUnitLoc = formatters.MEASURE_UNITS.get(measureName, '')
        unitOfMeasurement = i18n.makeString(measureUnitLoc) if i18n.isValidKey(measureUnitLoc) else ''
        moduleModel.setDescription(backport.text(R.strings.menu.moduleInfo.params.dyn(titleName)()))
        moduleModel.setUnitOfMeasurement(unitOfMeasurement)

    def __getValuesAndStates(self, paramInfo):
        values = []
        states = []
        from collections import Iterable
        if isinstance(paramInfo.value, Iterable):
            for i in range(len(paramInfo.state)):
                if paramInfo.value[i] in values:
                    continue
                if isinstance(paramInfo.value[i], Iterable):
                    values.append(paramInfo.value[i][0])
                    states.append(paramInfo.state[i])
                if paramInfo.value[i] is None:
                    continue
                values.append(paramInfo.value[i])
                states.append(paramInfo.state[i])

        else:
            values = [paramInfo.value]
            states = [paramInfo.state]
        return (values, states)

    def __fillModuleDescription(self, moduleModel, values, states, frmValue=None):
        parametersArray = Array()
        if frmValue is not None:
            parameterModel = ParametersValues()
            parameterModel.setValue(frmValue)
            parametersArray.addViewModel(parameterModel)
        else:
            for i, value in enumerate(values):
                parameterModel = ParametersValues()
                if isinstance(value, float):
                    integerPart = int(value)
                    fractionalPart = value - integerPart
                    if fractionalPart == 0.0:
                        value = integerPart
                    else:
                        value = round(value, 2)
                parameterModel.setValue(str(value))
                stateType, _ = states[i]
                if stateType == PARAM_STATE.WORSE:
                    parameterModel.setIsWorst(True)
                elif stateType == PARAM_STATE.BETTER:
                    parameterModel.setIsBetter(True)
                parametersArray.addViewModel(parameterModel)

        moduleModel.setValues(parametersArray)
        return

    def __getPortalTreeModuleSettings(self, vModule):
        realDescriptorId = vModule.name
        if realDescriptorId.endswith('_H'):
            fakeDescriptorId = realDescriptorId[:-2] + '_SH'
        else:
            fakeDescriptorId = realDescriptorId
        data = getBattleRoyaleSettings().techTree.modules.get(fakeDescriptorId)
        return None if not data else data

    def __floatToPercentage(self, value):
        percentage = (value - 1.0) * 100
        rounded = int(round(percentage))
        if rounded > 0:
            return '+%d%%' % rounded
        return '%d%%' % rounded if rounded < 0 else '0%'

    def __getMaxHealthDifference(self, currModule, module, vehicle):
        typeCDCurrentModule = getTypeOfCompactDescr(currModule.intCD)
        typeCDNewModule = getTypeOfCompactDescr(module.intCD)
        difference = 0
        if typeCDCurrentModule == GUI_ITEM_TYPE.CHASSIS and typeCDNewModule == GUI_ITEM_TYPE.CHASSIS:
            defaultHull = vehicle.typeDescr.hulls[0]
            newNull = [ hull for hull in vehicle.typeDescr.hulls if module.innationID in hull.variantMatch ]
            newNull = newNull[0] if newNull else None
            if newNull:
                difference = newNull.maxHealth - defaultHull.maxHealth
        elif typeCDCurrentModule == GUI_ITEM_TYPE.TURRET and typeCDNewModule == GUI_ITEM_TYPE.TURRET:
            if module.descriptor.level != currModule.descriptor.level:
                difference = module.descriptor.maxHealth - currModule.descriptor.maxHealth
            else:
                defaultTurret = vehicle.typeDescr.turrets[0][0]
                difference = module.descriptor.maxHealth - defaultTurret.maxHealth
        return difference
