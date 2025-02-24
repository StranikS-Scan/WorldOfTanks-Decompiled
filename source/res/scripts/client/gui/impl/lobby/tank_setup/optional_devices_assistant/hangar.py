# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/optional_devices_assistant/hangar.py
from enum import IntEnum
from functools import partial
import typing
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, OptionalDevicesAssistant
from constants import QUEUE_TYPE
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_item import OptionalDevicesAssistantItem as ODAItem
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_model import OptionalDevicesAssistantStateEnum, OptionalDevicesAssistantItemType
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset import OptionalDevicesAssistantPreset as OptDeviceAssistPresetUI, OptionalDevicesAssistantModeTypeEnum
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset import OptionalDevicesAssistantTypeEnum as OdaUItype
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_preset_model_type import OptionalDevicesAssistantPresetTypeEnum as PresetType
from gui.impl.gui_decorators import args2params
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from renewable_subscription_common.optional_devices_usage_config import GenericOptionalDevice
from skeletons.gui.game_control import IOptionalDevicesAssistantController, IComp7Controller
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Set
    from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_model import OptionalDevicesAssistantModel
    from renewable_subscription_common.optional_devices_usage_config import VehicleLoadout
_GENERIC_INT_TYPE_TO_UI_ENUM = {GenericOptionalDevice.STEREOSCOPE: OptionalDevicesAssistantItemType.STEREOSCOPE,
 GenericOptionalDevice.TURBOCHARGER: OptionalDevicesAssistantItemType.TURBOCHARGER,
 GenericOptionalDevice.ENHANCED_AIM_DRIVES: OptionalDevicesAssistantItemType.ENHANCEDAIMDRIVES,
 GenericOptionalDevice.GROUSERS: OptionalDevicesAssistantItemType.GROUSERS,
 GenericOptionalDevice.AIMING_STABILIZER: OptionalDevicesAssistantItemType.AIMINGSTABILIZER,
 GenericOptionalDevice.ANTIFRAGMENTATION_LINING: OptionalDevicesAssistantItemType.ANTIFRAGMENTATIONLINING,
 GenericOptionalDevice.CAMOUFLAGE_NET: OptionalDevicesAssistantItemType.CAMOUFLAGENET,
 GenericOptionalDevice.IMPROVED_SIGHTS: OptionalDevicesAssistantItemType.IMPROVEDSIGHTS,
 GenericOptionalDevice.VENTILATION: OptionalDevicesAssistantItemType.VENTILATION,
 GenericOptionalDevice.HEALTH_RESERVE: OptionalDevicesAssistantItemType.HEALTHRESERVE,
 GenericOptionalDevice.ROTATION_MECHANISM: OptionalDevicesAssistantItemType.ROTATIONMECHANISM,
 GenericOptionalDevice.RAMMER: OptionalDevicesAssistantItemType.RAMMER,
 GenericOptionalDevice.COATED_OPTICS: OptionalDevicesAssistantItemType.COATEDOPTICS,
 GenericOptionalDevice.ADDIT_INVISIBILITY_DEVICE: OptionalDevicesAssistantItemType.ADDITINVISIBILITYDEVICE,
 GenericOptionalDevice.IMPROVED_CONFIGURATION: OptionalDevicesAssistantItemType.IMPROVEDCONFIGURATION,
 GenericOptionalDevice.RADIO_COMMUNICATION: OptionalDevicesAssistantItemType.RADIOCOMMUNICATION,
 GenericOptionalDevice.COMMANDERS_VIEW: OptionalDevicesAssistantItemType.COMMANDERSVIEW,
 GenericOptionalDevice.MODERNIZED_EXTRA_HEALTH_RESERVE_ANTIFRAGMENTATION_LINING: OptionalDevicesAssistantItemType.MODERNIZEDEXTRAHEALTHRESERVEANTIFRAGMENTATIONLINING,
 GenericOptionalDevice.MODERNIZED_TURBOCHARGER_ROTATION_MECHANISM: OptionalDevicesAssistantItemType.MODERNIZEDTURBOCHARGERROTATIONMECHANISM,
 GenericOptionalDevice.MODERNIZED_AIM_DRIVES_AIMING_STABILIZER: OptionalDevicesAssistantItemType.MODERNIZEDAIMDRIVESAIMINGSTABILIZER,
 GenericOptionalDevice.MODERNIZED_IMPROVED_SIGHTS_ENHANCED_AIM_DRIVES: OptionalDevicesAssistantItemType.MODERNIZEDIMPROVEDSIGHTSENHANCEDAIMDRIVES}
_ARCHETYPE_TO_TAG_ENUM = {GenericOptionalDevice.MODERNIZED_EXTRA_HEALTH_RESERVE_ANTIFRAGMENTATION_LINING: OptionalDevicesAssistantItemType.HEALTHRESERVE,
 GenericOptionalDevice.MODERNIZED_TURBOCHARGER_ROTATION_MECHANISM: OptionalDevicesAssistantItemType.TURBOCHARGER,
 GenericOptionalDevice.MODERNIZED_AIM_DRIVES_AIMING_STABILIZER: OptionalDevicesAssistantItemType.ENHANCEDAIMDRIVES,
 GenericOptionalDevice.MODERNIZED_IMPROVED_SIGHTS_ENHANCED_AIM_DRIVES: OptionalDevicesAssistantItemType.IMPROVEDSIGHTS}
_LAST_ORDER_VALUE = 1000
_LAST_MODERNIZED_ORDER_VALUE = 1001

class OptDeviceAssistType(IntEnum):
    NODATA = 0
    NORMAL = 1
    LINKED = 2
    COMBINED = 3


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _sortComparator(categories, device, itemsCache=None):
    deviceKey = _GENERIC_INT_TYPE_TO_UI_ENUM[device].value
    criteria = REQ_CRITERIA.OPTIONAL_DEVICE.MODERNIZED | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_BY_ARCHETYPE(deviceKey)
    modernizedDevices = itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
    if modernizedDevices:
        return _LAST_MODERNIZED_ORDER_VALUE
    if categories:
        criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_TAGS({deviceKey}) | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_FROM_CATEGORIES(categories)
        optDevices = itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria).values()
        if not optDevices:
            return _LAST_ORDER_VALUE
        categoriesSet = set().union(*(optDevice.descriptor.categories for optDevice in optDevices))
        return len(categoriesSet)


def _sortDevices(vehicle, loadout):
    if len(vehicle.optDevices.slots) != 3:
        return loadout.devices
    slotCategories = vehicle.optDevices.getSlot(1).item.categories
    loadoutDevicesCopy = list(loadout.devices)
    sortedDevices = [loadoutDevicesCopy.pop(0)]
    loadoutDevicesCopy.sort(key=partial(_sortComparator, slotCategories))
    sortedDevices.extend(loadoutDevicesCopy)
    return sortedDevices


class OptionalDevicesAssistantView(BaseSubModelView):
    __slots__ = ('_queueType',)
    _optionalDevicesAssistantCtrl = dependency.descriptor(IOptionalDevicesAssistantController)
    _comp7onslaughtCtrl = dependency.descriptor(IComp7Controller)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, queueType):
        super(OptionalDevicesAssistantView, self).__init__(viewModel)
        self._queueType = queueType
        self.viewModel.setIsHintShown(AccountSettings.getSettings(OptionalDevicesAssistant.HINT_SHOWN))

    @property
    def viewModel(self):
        return self._viewModel

    def onLoading(self, *args, **kwargs):
        super(OptionalDevicesAssistantView, self).onLoading(*args, **kwargs)
        self._fillModel()

    def updateVehicle(self, _):
        self._fillModel()

    def __onHintShown(self, _):
        if not AccountSettings.getSettings(OptionalDevicesAssistant.HINT_SHOWN):
            AccountSettings.setSettings(OptionalDevicesAssistant.HINT_SHOWN, True)
            self.viewModel.setIsHintShown(True)

    @args2params(int)
    def __onPresetSelected(self, presetType):
        AccountSettings.setSettings(OptionalDevicesAssistant.SELECTED_PRESET, presetType)

    def _fillModel(self):
        currentVehicle = g_currentVehicle.item
        if not self.__isSuitableVehicle(currentVehicle):
            self.viewModel.setState(OptionalDevicesAssistantStateEnum.NOTSUITABLEVEHICLE)
            return
        if not self.__isVehicleDataAvailable(currentVehicle):
            self.viewModel.setState(OptionalDevicesAssistantStateEnum.NODATAATALL)
            return
        qt = self._queueType
        if self._queueType == QUEUE_TYPE.COMP7:
            qt = QUEUE_TYPE.RANDOMS
        commonData, legendaryData = self._optionalDevicesAssistantCtrl.getPopularOptDevicesPresets(currentVehicle, qt)
        if commonData[0] == OptDeviceAssistType.NODATA and legendaryData[0] == OptDeviceAssistType.NODATA:
            self.viewModel.setState(OptionalDevicesAssistantStateEnum.NODATAATALL)
            return
        with self.viewModel.transaction() as tx:
            tx.setState(OptionalDevicesAssistantStateEnum.VISIBLE)
            storedPresetVal = AccountSettings.getSettings(OptionalDevicesAssistant.SELECTED_PRESET)
            tx.selectedPreset.setMType(PresetType(storedPresetVal))
            items = tx.getOptionalDevicesAssistantPresets()
            items.clear()
            items.reserve(2)
            items.addViewModel(self.__createPreset(currentVehicle, PresetType.COMMON, *commonData))
            items.addViewModel(self.__createPreset(currentVehicle, PresetType.LEGENDARY, *legendaryData))
            items.invalidate()

    def _addListeners(self):
        super(OptionalDevicesAssistantView, self)._addListeners()
        self._optionalDevicesAssistantCtrl.onConfigChanged += self.__onDataChanged
        self.viewModel.onHintShown += self.__onHintShown
        self.viewModel.onPresetSelected += self.__onPresetSelected

    def _removeListeners(self):
        super(OptionalDevicesAssistantView, self)._removeListeners()
        self._optionalDevicesAssistantCtrl.onConfigChanged -= self.__onDataChanged
        self.viewModel.onPresetSelected -= self.__onPresetSelected

    def _fillVehicleLoadoutsData(self, vehicle, loadouts):
        popularItemsData = []
        for loadout in loadouts:
            sortedDevices = _sortDevices(vehicle, loadout)
            popularItem = ODAItem()
            popularItem.setPopularity(loadout.percentage)
            loadoutItems = popularItem.getItems()
            loadoutItems.reserve(len(sortedDevices))
            for device in sortedDevices:
                loadoutItems.addString(_GENERIC_INT_TYPE_TO_UI_ENUM[device].value)

            popularItemsData.append(popularItem)

        return popularItemsData

    def __onDataChanged(self):
        self._fillModel()

    def __isSuitableVehicle(self, vehicle):
        if self._queueType == QUEUE_TYPE.RANDOMS:
            return vehicle.getState()[0] != Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE
        elif self._queueType == QUEUE_TYPE.COMP7:
            suitableVehResult = self._comp7onslaughtCtrl.isSuitableVehicle(vehicle)
            return suitableVehResult is None or suitableVehResult.isValid
        else:
            return True

    def __isVehicleDataAvailable(self, vehicle):
        if self._queueType == QUEUE_TYPE.RANDOMS:
            return not vehicle.isSecret
        return not vehicle.isSecret or vehicle.isOnlyForComp7Battles if self._queueType == QUEUE_TYPE.COMP7 else True

    def __createPreset(self, vehicle, presetType, resultType, resultVehicle, loadouts):
        preset = OptDeviceAssistPresetUI()
        preset.presetType.setMType(presetType)
        preset.setOptionalDevicesResultType(OdaUItype(resultType))
        preset.setSourceVehicleCompDescr(resultVehicle)
        uiLoadouts = self._fillVehicleLoadoutsData(vehicle, loadouts)
        items = preset.getOptionalDevicesAssistantItems()
        items.reserve(len(uiLoadouts))
        for item in uiLoadouts:
            items.addViewModel(item)

        qt = OptionalDevicesAssistantModeTypeEnum.UNKNOWN
        if self._queueType == QUEUE_TYPE.RANDOMS:
            qt = OptionalDevicesAssistantModeTypeEnum.RANDOM
        elif self._queueType == QUEUE_TYPE.COMP7:
            qt = OptionalDevicesAssistantModeTypeEnum.COMP7
        preset.setModeType(qt)
        return preset
