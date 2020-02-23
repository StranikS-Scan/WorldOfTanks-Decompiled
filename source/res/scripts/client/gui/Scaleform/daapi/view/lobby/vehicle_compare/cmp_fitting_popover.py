# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_fitting_popover.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover import PopoverLogicProvider, CommonFittingSelectPopover, BattleBoosterSelectPopover, OptionalDeviceSelectPopover
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA as _RC
_NOT_AFFECTED_TEXT = text_styles.alert(VEH_COMPARE.VEHCONF_DOESNTAFFECT)
_POPOVER_FIRST_TAB_IDX = 0
_POPOVER_SECOND_TAB_IDX = 1

class VehCmpBattleBoosterSelectPopover(BattleBoosterSelectPopover):

    def __init__(self, ctx=None):
        self.__initialLoad = True
        self.cmpVeh = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicle()
        super(VehCmpBattleBoosterSelectPopover, self).__init__(ctx, lambda slotType, slotIndex: _CmpVehBattleBoosterLogicProvider(slotType, slotIndex, self.cmpVeh))

    def _prepareInitialData(self):
        result = super(VehCmpBattleBoosterSelectPopover, self)._prepareInitialData()
        result['rearmCheckboxVisible'] = False
        return result

    def _getCommonData(self):
        return (FITTING_TYPES.BOOSTER_FITTING_ITEM_RENDERER,
         FITTING_TYPES.BOOSTER_FITTING_RENDERER_DATA_CLASS_NAME,
         FITTING_TYPES.LARGE_POPOVER_WIDTH,
         MENU.BOOSTERSELECTPOPOVER_TITLE)

    def _getTabCounters(self):
        return [0, 0]

    def _getVehicle(self):
        return self.cmpVeh


class VehCmpOptionalDeviceSelectPopover(OptionalDeviceSelectPopover):

    def __init__(self, ctx=None):
        self.__initialLoad = True
        self.cmpVeh = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicle()
        super(VehCmpOptionalDeviceSelectPopover, self).__init__(ctx, lambda slotType, slotIndex: _CmpVehOptDevicesLogicProvider(slotType, slotIndex, self.cmpVeh))

    def _getVehicle(self):
        return self.cmpVeh


class _CmpVehBattleBoosterLogicProvider(PopoverLogicProvider):

    def __init__(self, slotType, slotIndex, vehicle):
        super(_CmpVehBattleBoosterLogicProvider, self).__init__(slotType, slotIndex, vehicle)
        self.__slotType = slotType
        self.__slotIndex = slotIndex
        self._tooltipType = TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_COMPARE

    def _buildModuleData(self, module, isInstalledInSlot, stats):
        isFit, reason = module.mayInstall(self._vehicle, self._slotIndex)
        moduleData = self._buildCommonModuleData(module, reason)
        isInstalled = module.isInstalled(self._vehicle)
        disabled = False
        if isInstalled:
            if not isInstalledInSlot:
                disabled = True
        else:
            disabled = not isFit
        moduleData['disabled'] = disabled
        moduleData['isSelected'] = isInstalledInSlot
        moduleData['targetVisible'] = isInstalled
        moduleData['removeButtonTooltip'] = VEH_COMPARE.VEHCONF_TOOLTIPS_BTNCLEANUP
        moduleData['showPrice'] = False
        return moduleData

    def setModule(self, newId, oldId, isRemove):
        cmp_config_view = cmp_helpers.getCmpConfiguratorMainView()
        if isRemove:
            cmp_config_view.removeBattleBooster()
        else:
            cmp_config_view.installBattleBooster(newId)

    def _buildList(self):
        moduleList = super(_CmpVehBattleBoosterLogicProvider, self)._buildList()
        for item in moduleList:
            item['removable'] = True
            item['removeButtonLabel'] = VEH_COMPARE.VEHCONF_BTNCLEANUP
            item['buyButtonVisible'] = False

        return moduleList


class VehCmpConfigSelectPopover(CommonFittingSelectPopover):

    def __init__(self, ctx=None):
        data_ = ctx['data']
        slotType = data_.slotType
        slotIndex = data_.slotIndex
        cmpVeh = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicle()
        if self.__isEquipment(slotType):
            logicProvider = _CmpVehEquipmentLogicProvider(slotType, slotIndex, cmpVeh)
        else:
            logicProvider = None
            LOG_ERROR('Unsupported slotType: {}'.format(slotType))
        super(VehCmpConfigSelectPopover, self).__init__(cmpVeh, logicProvider, ctx)
        return

    def _getCommonData(self):
        return (FITTING_TYPES.OPTIONAL_DEVICE_FITTING_ITEM_RENDERER,
         FITTING_TYPES.OPTIONAL_DEVICE_RENDERER_DATA_CLASS_NAME,
         FITTING_TYPES.LARGE_POPOVER_WIDTH,
         MENU.EQUIPMENTFITS_TITLE) if self.__isEquipment(self._slotType) else super(VehCmpConfigSelectPopover, self)._getCommonData()

    @staticmethod
    def __isEquipment(slotType):
        return slotType == cmp_helpers.EQUIPMENT_TYPE_NAME


class _CmpVehArtefactLogicProvider(PopoverLogicProvider):

    def __init__(self, slotType, slotIndex, vehicle, notAffectedArtefacts):
        super(_CmpVehArtefactLogicProvider, self).__init__(slotType, slotIndex, vehicle)
        self._notAffectedArtefacts = notAffectedArtefacts

    def setModule(self, newId, oldId, isRemove):
        cmp_config_view = cmp_helpers.getCmpConfiguratorMainView()
        if isRemove:
            self._removeArtifact(cmp_config_view, self._slotIndex)
        else:
            self._installArtifact(cmp_config_view, newId, self._slotIndex)

    def _removeArtifact(self, cmp_config_view, slotIndex):
        pass

    def _installArtifact(self, cmp_config_view, newId, slotIndex):
        pass

    def _sortNotAffected(self, artefacts):

        def sortByAffectedVal(item):
            return len(item.tags.intersection(self._notAffectedArtefacts)) > 0

        return sorted(artefacts, key=sortByAffectedVal)

    def _isNotAffected(self, module):
        return len(module.tags.intersection(self._notAffectedArtefacts)) > 0

    def _buildModuleData(self, module, isInstalledInSlot, stats):
        isFit, reason = module.mayInstall(self._vehicle, self._slotIndex)
        moduleData = self._buildCommonModuleData(module, reason)
        isNotAffected = self._isNotAffected(module)
        isInstalled = module.isInstalled(self._vehicle)
        disabled = False
        if isInstalled:
            if not isInstalledInSlot:
                disabled = True
        else:
            disabled = not isFit
        moduleData['disabled'] = disabled
        moduleData['isSelected'] = isInstalledInSlot
        moduleData['targetVisible'] = isInstalled
        moduleData['removeButtonLabel'] = VEH_COMPARE.VEHCONF_BTNCLEANUP
        moduleData['removeButtonTooltip'] = VEH_COMPARE.VEHCONF_TOOLTIPS_BTNCLEANUP
        moduleData['notAffectedTTC'] = isNotAffected
        moduleData['showPrice'] = False
        if isNotAffected:
            moduleData['status'] = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON)
            moduleData['notAffectedTTCTooltip'] = makeTooltip(module.userName, attention=VEH_COMPARE.VEHCONF_TOOLTIPS_DEVICENOTAFFECTEDTTC)
        return moduleData

    def _buildList(self):
        moduleList = super(_CmpVehArtefactLogicProvider, self)._buildList()
        for item in moduleList:
            item['removable'] = True
            item['isUpgradable'] = False

        return moduleList

    def _getSuitableItems(self, typeId):
        return self._sortNotAffected(super(_CmpVehArtefactLogicProvider, self)._getSuitableItems(typeId))


class _CmpVehOptDevicesLogicProvider(_CmpVehArtefactLogicProvider):

    def __init__(self, slotType, slotIndex, vehicle):
        super(_CmpVehOptDevicesLogicProvider, self).__init__(slotType, slotIndex, vehicle, cmp_helpers.NOT_AFFECTED_DEVICES)
        self._tooltipType = TOOLTIPS_CONSTANTS.COMPARE_MODULE

    def _getSpecificCriteria(self, typeID):
        criteria = super(_CmpVehOptDevicesLogicProvider, self)._getSpecificCriteria(typeID)
        if self._tabIndex == _POPOVER_FIRST_TAB_IDX:
            invVehicles = self._itemsCache.items.getVehicles(_RC.INVENTORY).values()
            upgradedOptDevCDs = self.__getUpgradedOptDevCDs(typeID, invVehicles)
            criteria = _RC.CUSTOM(lambda item: item.intCD in upgradedOptDevCDs or not item.isDeluxe)
        return criteria

    def _removeArtifact(self, cmp_config_view, slotIndex):
        cmp_config_view.removeOptionalDevice(slotIndex)

    def _installArtifact(self, cmp_config_view, newId, slotIndex):
        cmp_config_view.installOptionalDevice(newId, slotIndex)

    def __getUpgradedOptDevCDs(self, typeID, invVehicles):
        criteria = _RC.VEHICLE.SUITABLE([self._vehicle], [typeID])
        criteria |= _RC.CUSTOM(lambda item: (item.inventoryCount > 0 or item.getInstalledVehicles(invVehicles)) and item.isUpgradable)
        upgradableOptDevs = self._itemsCache.items.getItems(typeID, criteria).values()
        upgradedOptDevCDs = []
        for optDev in upgradableOptDevs:
            upgradedCompDescr = optDev.descriptor.upgradeInfo.upgradedCompDescr
            upgradedOptDevCDs.append(upgradedCompDescr)

        return upgradedOptDevCDs


class _CmpVehEquipmentLogicProvider(_CmpVehArtefactLogicProvider):

    def __init__(self, slotType, slotIndex, vehicle):
        super(_CmpVehEquipmentLogicProvider, self).__init__(slotType, slotIndex, vehicle, cmp_helpers.NOT_AFFECTED_EQUIPMENTS)
        self._tooltipType = TOOLTIPS_CONSTANTS.COMPARE_MODULE

    def _getSpecificCriteria(self, _):
        return ~_RC.HIDDEN

    def _removeArtifact(self, cmp_config_view, slotIndex):
        cmp_config_view.removeEquipment(slotIndex)

    def _installArtifact(self, cmp_config_view, newId, slotIndex):
        cmp_config_view.installEquipment(newId, slotIndex)
