# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/data_providers/opt_devices_data_provider.py
import logging
from collections import OrderedDict
from enum import Enum
from typing import TYPE_CHECKING
from gui.game_control.wotlda.loadout_model import BaseOptDeviceLoadoutModel
from gui.goodies.demount_kit import isDemountKitApplicableTo, getDemountKitForOptDevice
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.preset_model import PresetDisableReason
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalDisableReason
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.opt_devices_preset_model import OptDevicesPresetType
from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider, PresetInfo, SlotInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IWotPlusController, IEasyTankEquipController
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import List, Optional, Dict
    from gui.goodies.goodie_items import DemountKit
    from gui.shared.gui_items.artefacts import OptionalDevice
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.gui_items.vehicle_equipment import OptDeviceSlotData
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.money import Money
_logger = logging.getLogger(__name__)

class OptionalDevicesPresetInfo(PresetInfo):

    def __init__(self, itemPrice, presetType, items, demountKits=0, installed=False, storedItemsCount=0, installedItemsCount=0, disableReason=PresetDisableReason.NONE):
        super(OptionalDevicesPresetInfo, self).__init__(installed, storedItemsCount, installedItemsCount, itemPrice)
        self.presetType = presetType
        self.items = items
        self.demountKits = demountKits
        self.disableReason = disableReason


class OptDevicesPresetSlotInfo(object):

    def __init__(self, optDevice, slotData, info, slotIdx):
        self.optDevice = optDevice
        self.slotIdx = slotIdx
        self.slotData = slotData
        self.info = info


class OptDevicesPriorities(Enum):
    MODERNIZED_LEVEL_3 = 0
    DELUXE_LEVEL_2 = 1
    DELUXE_LEVEL_1 = 2
    TROPHY_UPGRADED = 3
    MODERNIZED_LEVEL_2 = 4
    MODERNIZED_LEVEL_1 = 5
    REGULAR = 6
    TROPHY_NOT_UPGRADED = 7


class OptDevicesDemountInfo(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    def __init__(self, forDemount):
        self.forDemount = forDemount or []
        self.byMoney = []
        self.byDemountKit = []
        self.forFree = []
        self.initialize()

    def initialize(self):
        demountKits = 0
        for optDevice in self.forDemount:
            if self.__wotPlusController.isFreeToDemount(optDevice):
                self.forFree.append(optDevice)
                continue
            if isDemountKitApplicableTo(optDevice):
                dk, _ = getDemountKitForOptDevice(optDevice)
                enoughDemountKits = dk.inventoryCount > demountKits
                if enoughDemountKits:
                    self.byDemountKit.append(optDevice)
                    demountKits += 1
                else:
                    self.byMoney.append(optDevice)
            self.byMoney.append(optDevice)

    def getDemountPrice(self):
        return (len(self.byDemountKit), sum([ device.getRemovalPrice(self.__itemsCache.items) for device in self.byMoney ], ITEM_PRICE_ZERO))


class OptDevicesDataProvider(BaseDataProvider):
    __itemsCache = dependency.descriptor(IItemsCache)
    __easyTankEquipController = dependency.descriptor(IEasyTankEquipController)

    def __init__(self, vehicle, balance):
        super(OptDevicesDataProvider, self).__init__(vehicle, balance)
        self.__installedOptDevices = self.vehicle.optDevices.installed
        self.__optDevicesCapacity = self.__installedOptDevices.getCapacity()
        self.__optDevicesPresets = OrderedDict()
        self.__optDevicesForDemount = OrderedDict()

    def initialize(self):
        super(OptDevicesDataProvider, self).initialize()
        if not self.__optDevicesPresets:
            self.proposalDisableReason = ProposalDisableReason.NOT_FORMED
            return
        self.currentPresetIndex, currentPreset = self._getCurrentPresetInfo(defaultIndex=self.currentPresetIndex)
        self.isProposalSelected = not (self.__installedOptDevices.getItems() or self.isCurrentPresetDisabledForApplying() or self.lastCheckedBalance.getShortage(currentPreset.itemPrice.price))

    def finalize(self):
        self.__installedOptDevices = None
        self.__optDevicesPresets.clear()
        self.__optDevicesForDemount.clear()
        super(OptDevicesDataProvider, self).finalize()
        return

    def setValuesFromCurrentPreset(self):
        devices = self.__optDevicesPresets.values()[self.currentPresetIndex]
        self.__installOptDevices(devices)

    def revertChangesFromSelectedPreset(self):
        devices = self.__installedOptDevices.getItems(ignoreEmpty=False)
        self.__installOptDevices(devices)

    def getPresets(self):
        self.__optDevicesPresets.clear()
        self.__optDevicesForDemount.clear()
        self.__setOptDevicesPresets()
        return self.__getPresetsInfo()

    def updatePresets(self, fullUpdate=False):
        presets = self.getPresets()
        self.presets = presets
        presetIndex = min(self.currentPresetIndex, len(presets) - 1)
        self.currentPresetIndex = presetIndex

    def swapSlots(self, firstSlot, secondSlot):
        presetItems = self.__optDevicesPresets.values()[self.currentPresetIndex]
        presetItems[firstSlot], presetItems[secondSlot] = presetItems[secondSlot], presetItems[firstSlot]
        self.presets = self.__getPresetsInfo()

    def isCurrentPresetDisableReasonChanged(self):
        presets = self.__getPresetsInfo()
        if presets and self.presets[self.currentPresetIndex].disableReason != presets[self.currentPresetIndex].disableReason:
            self.presets = presets
            return True
        return False

    def getCurrentPresetItemsIds(self):
        if self.isProposalDisabled():
            return []
        return [ optDevice.intCD for optDevice in self.__optDevicesPresets.values()[self.currentPresetIndex] ]

    def _getPresetDataForApplying(self):
        data = super(OptDevicesDataProvider, self)._getPresetDataForApplying()
        demountInfo = self.__optDevicesForDemount.values()[self.currentPresetIndex]
        data.update({'optDevices': self.__optDevicesPresets.values()[self.currentPresetIndex],
         'demountByDemountKit': demountInfo.byDemountKit,
         'demountForFree': demountInfo.forFree})
        return data

    def __getPresetsInfo(self):
        return [ self.__getOptDevicesPresetInfo(presetType, items) for presetType, items in self.__optDevicesPresets.items() ]

    def __presetIsTooHeavy(self, presetType):
        optDevsSequence = [ optDevice.intCD for optDevice in self.__optDevicesPresets[presetType] ]
        installPossible, reason = self.vehicle.descriptor.mayInstallOptDevsSequence(optDevsSequence)
        return True if not installPossible and 'too heavy' in reason else False

    def __isAdvancedPresetNeeded(self, optDevices):
        if len(optDevices) != self.__optDevicesCapacity or not all(optDevices):
            return False
        standardPreset = self.__optDevicesPresets[OptDevicesPresetType.STANDARD]
        if not standardPreset:
            return True
        return any([ device1.intCD != device2.intCD for device1, device2 in zip(standardPreset, optDevices) ])

    def __isStandardPresetNeeded(self, optDevices):
        return len(optDevices) == self.__optDevicesCapacity and all(optDevices)

    def __setOptDevicesPresets(self):
        loadout = self.__easyTankEquipController.getLoadoutByVehicleID(self.vehicle.intCD)
        if not loadout:
            _logger.warning('No easy tank loadouts were found for vehicle %d.', self.vehicle.intCD)
            return
        standardLoadoutDevices = loadout.getDevices()
        modernizedLoadoutDevices = loadout.getDevices(getModernized=True)
        standardOptDevices = self.__getStandardOptDevices(standardLoadoutDevices)
        upgradedOptDevices = self.__getAdvancedOptDevices(standardLoadoutDevices, standardOptDevices)
        modernizedOptDevices = self.__getAdvancedOptDevices(modernizedLoadoutDevices, standardOptDevices)
        advancedOptDevices = [ (device1 if self.__getOptDeviceIndex(device1) < self.__getOptDeviceIndex(device2) else device2) for device1, device2 in zip(modernizedOptDevices, upgradedOptDevices) ]
        if self.__isStandardPresetNeeded(standardOptDevices):
            self.__optDevicesPresets[OptDevicesPresetType.STANDARD] = standardOptDevices
            self.__optDevicesForDemount[OptDevicesPresetType.STANDARD] = self.__getOptDevicesForDemount(standardOptDevices)
        if self.__isAdvancedPresetNeeded(advancedOptDevices):
            self.__optDevicesPresets[OptDevicesPresetType.ADVANCED] = advancedOptDevices
            self.__optDevicesForDemount[OptDevicesPresetType.ADVANCED] = self.__getOptDevicesForDemount(advancedOptDevices)

    def __getOptDevicesPresetInfo(self, presetType, optDevices):
        installed = self.__isOptDevicesPresetInstalled(optDevices)
        if installed:
            return self.__getInstalledPresetInfo(presetType)
        presetItems = self.__getOptDevicesPresetItems(optDevices)
        if self.__presetIsTooHeavy(presetType):
            return self.__getIsTooHeavyPresetInfo(presetType, presetItems)
        demountKits, demountItemsPrice = self.__optDevicesForDemount[presetType].getDemountPrice()
        if self.__itemsCache.items.stats.money.getShortage(demountItemsPrice.price):
            return self.__getDemountNotPossiblePresetInfo(presetType, presetItems, demountItemsPrice, demountKits)
        return OptionalDevicesPresetInfo(installed=installed, storedItemsCount=len([ item for item in presetItems if item.info.storedItemsCount > 0 ]), installedItemsCount=len([ item for item in presetItems if item.info.installedItemsCount > 0 ]), itemPrice=sum([ item.info.itemPrice for item in presetItems ], ITEM_PRICE_ZERO) + demountItemsPrice, demountKits=demountKits, presetType=presetType, items=presetItems)

    def __getOptDevicesPresetItems(self, optDevices):
        return [ OptDevicesPresetSlotInfo(optDevice=optDevice, slotData=self.vehicle.optDevices.getSlot(slotIdx), info=self.__getSlotInfo(optDevice), slotIdx=slotIdx) for slotIdx, optDevice in enumerate(optDevices) ]

    def __getSlotInfo(self, optDevice):
        optDeviceOnVehicleCount = int(self.vehicle.optDevices.setupLayouts.containsIntCD(optDevice.intCD))
        optDeviceInventoryCount = min(optDevice.inventoryCount, 1) if optDeviceOnVehicleCount == 0 else 0
        needToBuyCount = int(optDeviceOnVehicleCount + optDeviceInventoryCount == 0)
        itemPrice = optDevice.getBuyPrice() * needToBuyCount
        return SlotInfo(storedItemsCount=optDeviceInventoryCount, installedItemsCount=optDeviceOnVehicleCount, itemPrice=itemPrice)

    def __isOptDevicesPresetInstalled(self, optDevices):
        return all([ self.__installedOptDevices.containsIntCD(optDevice.intCD) for optDevice in optDevices ])

    def __getOptDevices(self, criteria):
        return self.__itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, criteria=criteria, nationID=self.vehicle.nationID).values()

    def __getAdvancedOptDevices(self, optDevicesTags, standardOptDevices):
        advancedOptDevices = []
        numberOfStandardOptDevices = len(standardOptDevices)
        for deviceIndex, deviceTag in enumerate(optDevicesTags):
            criteria = REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_BY_ARCHETYPE(deviceTag) | REQ_CRITERIA.OPTIONAL_DEVICE.IS_COMPATIBLE_WITH_VEHICLE(self.vehicle)
            criteria |= REQ_CRITERIA.CUSTOM(lambda device: device.inventoryCount > 0 or self.vehicle.optDevices.setupLayouts.containsIntCD(device.intCD))
            optDevices = self.__getOptDevices(criteria)
            highestPriorityDevice = None
            indexExistInStandardPreset = deviceIndex < numberOfStandardOptDevices
            if optDevices:
                highestPriorityDevice = sorted(optDevices, key=self.__getOptDeviceIndex)[0]
                isTrophyNotUpgraded = highestPriorityDevice.isTrophy and highestPriorityDevice.isUpgradable
                if isTrophyNotUpgraded and indexExistInStandardPreset:
                    highestPriorityDevice = standardOptDevices[deviceIndex]
            elif indexExistInStandardPreset:
                highestPriorityDevice = standardOptDevices[deviceIndex]
            advancedOptDevices.append(highestPriorityDevice)

        return advancedOptDevices

    def __getStandardOptDevices(self, optDevicesTags):
        standardOptDevices = []
        for deviceTag in optDevicesTags:
            criteria = REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE | REQ_CRITERIA.OPTIONAL_DEVICE.HAS_ANY_BY_ARCHETYPE(deviceTag) | REQ_CRITERIA.OPTIONAL_DEVICE.IS_COMPATIBLE_WITH_VEHICLE(self.vehicle)
            standardOptDevices.append(first(self.__getOptDevices(criteria)))

        return standardOptDevices

    def __getOptDevicesForDemount(self, optDevices):
        return OptDevicesDemountInfo([ optDevice for optDevice in self.__installedOptDevices.getItems() if optDevice not in optDevices ])

    def __getInstalledPresetInfo(self, presetType):
        presetItems = self.__getOptDevicesPresetItems(self.__installedOptDevices.getItems())
        return OptionalDevicesPresetInfo(installed=True, installedItemsCount=len(presetItems), itemPrice=ITEM_PRICE_ZERO, presetType=presetType, items=presetItems)

    @staticmethod
    def __getIsTooHeavyPresetInfo(presetType, presetItems):
        return OptionalDevicesPresetInfo(itemPrice=ITEM_PRICE_ZERO, presetType=presetType, items=presetItems, disableReason=PresetDisableReason.LOAD_CAPACITY_NOT_ENOUGH)

    @staticmethod
    def __getDemountNotPossiblePresetInfo(presetType, presetItems, demountItemsPrice, demountKits):
        return OptionalDevicesPresetInfo(itemPrice=demountItemsPrice, demountKits=demountKits, presetType=presetType, items=presetItems, disableReason=PresetDisableReason.DEMOUNT_NOT_POSSIBLE)

    @staticmethod
    def __getOptDeviceIndex(optDevice):
        if optDevice.isModernized:
            if optDevice.level == 3:
                return OptDevicesPriorities.MODERNIZED_LEVEL_3.value
            if optDevice.level == 2:
                return OptDevicesPriorities.MODERNIZED_LEVEL_2.value
            return OptDevicesPriorities.MODERNIZED_LEVEL_1.value
        if optDevice.isDeluxe:
            if optDevice.level == 2:
                return OptDevicesPriorities.DELUXE_LEVEL_2.value
            return OptDevicesPriorities.DELUXE_LEVEL_1.value
        if optDevice.isTrophy:
            if optDevice.isUpgraded:
                return OptDevicesPriorities.TROPHY_UPGRADED.value
            return OptDevicesPriorities.REGULAR.value
        return OptDevicesPriorities.TROPHY_NOT_UPGRADED.value

    def __installOptDevices(self, devices):
        for idx in range(self.__optDevicesCapacity):
            self.vehicle.descriptor.removeOptionalDevice(idx, False)

        self.vehicle.optDevices.setLayout(*devices)
        self.vehicle.optDevices.setInstalled(*devices)
        self.vehicle.descriptor.installOptDevsSequence([ (optDevice.intCD if optDevice is not None else 0) for optDevice in devices ])
        return
