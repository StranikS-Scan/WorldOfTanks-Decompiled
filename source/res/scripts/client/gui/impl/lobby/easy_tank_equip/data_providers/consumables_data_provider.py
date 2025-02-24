# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/data_providers/consumables_data_provider.py
import logging
from collections import OrderedDict
from typing import TYPE_CHECKING, NamedTuple, List
from account_helpers.AccountSettings import EasyTankEquip
from gui.easy_tank_equip.easy_tank_equip_helpers import getEasyTankEquipSetting, setEasyTankEquipSetting
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.consumables_preset_model import ConsumablesPresetType
from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider, PresetInfo, SlotInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from gui.shared.gui_items.artefacts import Equipment
    from typing import Dict, Optional
_logger = logging.getLogger(__name__)
ConsumableTagsInfo = NamedTuple('ConsumableTagsInfo', [('includedTags', List[str]), ('excludedTags', List[str])])

class ConsumablesPresetSlotInfo(object):

    def __init__(self, consumable, info, slotIdx):
        self.consumable = consumable
        self.slotIdx = slotIdx
        self.info = info


class ConsumablesPresetInfo(PresetInfo):

    def __init__(self, installed, storedItemsCount, installedItemsCount, itemPrice, presetType, items):
        super(ConsumablesPresetInfo, self).__init__(installed, storedItemsCount, installedItemsCount, itemPrice)
        self.presetType = presetType
        self.items = items


class ConsumablesDataProvider(BaseDataProvider):
    DEFAULT_CONFIG = {ConsumablesPresetType.STANDARD: [ConsumableTagsInfo(includedTags=['medkit'], excludedTags=['premium_equipment']), ConsumableTagsInfo(includedTags=['repairkit'], excludedTags=['premium_equipment']), ConsumableTagsInfo(includedTags=['extinguisher'], excludedTags=['premium_equipment'])],
     ConsumablesPresetType.ADVANCED: [ConsumableTagsInfo(includedTags=['medkit', 'premium_equipment'], excludedTags=[]), ConsumableTagsInfo(includedTags=['repairkit', 'premium_equipment'], excludedTags=[]), ConsumableTagsInfo(includedTags=['extinguisher', 'premium_equipment'], excludedTags=[])],
     ConsumablesPresetType.IMPROVED: [ConsumableTagsInfo(includedTags=['medkit', 'premium_equipment'], excludedTags=[]), ConsumableTagsInfo(includedTags=['repairkit', 'premium_equipment'], excludedTags=[]), ConsumableTagsInfo(includedTags=['stimulator', 'premium_equipment'], excludedTags=[])]}
    REPLACE_CONSUMABLES_MAP = [(ConsumableTagsInfo(includedTags=['extinguisher'], excludedTags=['premium_equipment']), ConsumableTagsInfo(includedTags=['extinguisher', 'premium_equipment'], excludedTags=[]))]
    PRESETS_ORDER = [ConsumablesPresetType.STANDARD, ConsumablesPresetType.ADVANCED, ConsumablesPresetType.IMPROVED]
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, balance):
        super(ConsumablesDataProvider, self).__init__(vehicle, balance)
        self.__consumablesOrder = getEasyTankEquipSetting(EasyTankEquip.CONSUMABLES_CARD_PRESET_SLOTS_ORDER)
        self.__installedConsumables = self.vehicle.consumables.installed
        self.__consumablesPresets = OrderedDict()

    def initialize(self):
        super(ConsumablesDataProvider, self).initialize()
        if not self.__consumablesPresets:
            return
        defaultPresetIndex = min(getEasyTankEquipSetting(EasyTankEquip.CONSUMABLES_CARD_SELECTED_PRESET_INDEX), len(self.presets) - 1)
        self.currentPresetIndex, currentPreset = self._getCurrentPresetInfo(defaultPresetIndex)
        self.isProposalSelected = len(self.__installedConsumables.getItems()) != self.__installedConsumables.getCapacity() and not (self.lastCheckedBalance.getShortage(currentPreset.itemPrice.price) or self.isCurrentPresetDisabledForApplying())

    def finalize(self):
        self.__consumablesOrder = []
        self.__installedConsumables = None
        self.__consumablesPresets.clear()
        super(ConsumablesDataProvider, self).finalize()
        return

    def setValuesFromCurrentPreset(self):
        consumables = self.__consumablesPresets.values()[self.currentPresetIndex]
        self.vehicle.consumables.setLayout(*consumables)
        self.vehicle.consumables.setInstalled(*consumables)

    def revertChangesFromSelectedPreset(self):
        consumables = self.__installedConsumables.getItems(ignoreEmpty=False)
        self.vehicle.consumables.setLayout(*consumables)
        self.vehicle.consumables.setInstalled(*consumables)

    def getPresets(self):
        self.__setConsumablesPresets(self.__getConsumablesPresetsConfig())
        return self.__getPresetsInfo()

    def updatePresets(self, fullUpdate=False):
        presets = self.getPresets() if fullUpdate else self.__getPresetsInfo()
        self.presets = presets
        presetIndex = min(self.currentPresetIndex, len(presets) - 1)
        self.currentPresetIndex = presetIndex

    def swapSlots(self, firstSlot, secondSlot):
        presetItems = self.__consumablesPresets.values()[self.currentPresetIndex]
        presetItems[firstSlot], presetItems[secondSlot] = presetItems[secondSlot], presetItems[firstSlot]
        self.__consumablesOrder[firstSlot], self.__consumablesOrder[secondSlot] = self.__consumablesOrder[secondSlot], self.__consumablesOrder[firstSlot]
        self.presets = self.__getPresetsInfo()

    def getCurrentPresetItemsIds(self):
        if self.isProposalDisabled():
            return []
        return [ consumable.intCD for consumable in self.__consumablesPresets.values()[self.currentPresetIndex] ]

    def saveAccountSettings(self):
        setEasyTankEquipSetting(EasyTankEquip.CONSUMABLES_CARD_SELECTED_PRESET_INDEX, self.currentPresetIndex)
        setEasyTankEquipSetting(EasyTankEquip.CONSUMABLES_CARD_PRESET_SLOTS_ORDER, self.__consumablesOrder)

    def _getPresetDataForApplying(self):
        data = super(ConsumablesDataProvider, self)._getPresetDataForApplying()
        data.update({'eqs': self.__consumablesPresets.values()[self.currentPresetIndex]})
        return data

    def __getPresetsInfo(self):
        return [ self.__getConsumablesPresetInfo(presetType, items) for presetType, items in self.__consumablesPresets.items() ]

    def __getConsumablesPresetInfo(self, presetType, consumables):
        installed = self.__isConsumablesPresetInstalled(consumables)
        if installed:
            consumables = self.__installedConsumables.getItems()
        presetItems = self.__getConsumablesPresetItems(consumables)
        storedItemsCount = len([ item for item in presetItems if item.info.storedItemsCount > 0 ])
        installedItemsCount = len([ item for item in presetItems if item.info.installedItemsCount > 0 ])
        itemPrice = sum([ item.info.itemPrice for item in presetItems ], ITEM_PRICE_ZERO)
        return ConsumablesPresetInfo(installed=installed, storedItemsCount=storedItemsCount, installedItemsCount=installedItemsCount, itemPrice=itemPrice, presetType=presetType, items=presetItems)

    def __getConsumablesPresetItems(self, consumables):
        return [ ConsumablesPresetSlotInfo(consumable=consumable, info=self.__getSlotInfo(consumable), slotIdx=slotIdx) for slotIdx, consumable in enumerate(consumables) ]

    def __getSlotInfo(self, consumable):
        consumableOnVehicleCount = int(self.vehicle.consumables.setupLayouts.containsIntCD(consumable.intCD))
        consumableInventoryCount = min(consumable.inventoryCount, 1) if consumableOnVehicleCount == 0 else 0
        consumableAvailableCount = consumableOnVehicleCount + consumableInventoryCount
        needToBuyCount = int(consumableAvailableCount == 0)
        itemPrice = consumable.getBuyPrice() * needToBuyCount
        return SlotInfo(storedItemsCount=consumableInventoryCount, installedItemsCount=consumableOnVehicleCount, itemPrice=itemPrice)

    def __isConsumablesPresetInstalled(self, consumables):
        preset = {consumable.intCD for consumable in consumables}
        installed = set(self.__installedConsumables.getIntCDs())
        return preset == installed

    def __getConsumablesPresetsConfig(self):
        return self.DEFAULT_CONFIG

    def __setConsumablesPresets(self, presetConfig):
        self.__consumablesPresets.clear()
        for presetType in self.PRESETS_ORDER:
            consumables = []
            allValid = True
            for itemTags in presetConfig.get(presetType, []):
                consumable = self.__getConsumable(itemTags)
                if not consumable:
                    allValid = False
                    break
                consumables.append(consumable)

            if consumables and allValid:
                self.__consumablesPresets[presetType] = consumables

        wasAdded = self.__addBuiltInConsumables()
        self.__cutPresetItems(hasBuiltIn=wasAdded)
        self.__replaceConsumables()
        self.__removeDuplicatePresets()
        self.__sortPresets()

    def __addBuiltInConsumables(self):
        wasAdded = False
        builtinConsumables = []
        builtInConsumablesIDs = self.vehicle.getBuiltInEquipmentIDs()
        for builtinIntCD in builtInConsumablesIDs:
            builtin = self.__itemsCache.items.getItemByCD(builtinIntCD)
            if not builtin:
                _logger.warning('Failed to get builtin gui item. IntCD: %s.', builtinIntCD)
                continue
            builtinConsumables.append(builtin)

        for builtin in builtinConsumables:
            for items in self.__consumablesPresets.values():
                indexToChange = next((index for index, item in enumerate(items) if builtin.tags.issuperset(item.tags)), None)
                if indexToChange is None:
                    _logger.warning('Failed to add builtin gui item to preset. IntCD: %s.', builtin.intCD)
                    indexToChange = self.__installedConsumables.index(builtin) or 0
                wasAdded = True
                items[indexToChange] = builtin

        return wasAdded

    def __cutPresetItems(self, hasBuiltIn=False):
        if not hasBuiltIn:
            length = len(self.vehicle.consumables.layout)
            for presetType, items in self.__consumablesPresets.items():
                self.__consumablesPresets[presetType] = items[:length]

            return
        for items in self.__consumablesPresets.values():
            excessItemsCount = len(items) - len(self.vehicle.consumables.layout)
            for __ in range(excessItemsCount):
                indexToRemove = len(items) - 1
                for index, item in enumerate(reversed(items)):
                    if not item.isBuiltIn:
                        indexToRemove -= index
                        break
                else:
                    _logger.warning('Builtin consumable was removed from preset. Index: %s.', indexToRemove)

                del items[indexToRemove]

    def __replaceConsumables(self):
        replacingItems = []
        for replacedItemTags, newItemTags in self.REPLACE_CONSUMABLES_MAP:
            replacedItem = self.__getConsumable(replacedItemTags)
            if not replacedItem:
                _logger.warning('Failed to get replaced gui item. IncludedTags: %s, excludedTags: %s.', replacedItemTags.includedTags, replacedItemTags.excludedTags)
                continue
            newItem = self.__getConsumable(newItemTags)
            if not newItem:
                _logger.warning('Failed to get new gui item for replace. IncludedTags: %s, excludedTags: %s.', newItemTags.includedTags, newItemTags.excludedTags)
                continue
            if newItem.inventoryCount == 0 and not self.__installedConsumables.containsIntCD(newItem.intCD):
                continue
            replacingItems.append((replacedItem, newItem))

        for replacedItem, newItem in replacingItems:
            for items in self.__consumablesPresets.values():
                indexesToChange = [ index for index, item in enumerate(items) if item.intCD == replacedItem.intCD ]
                for index in indexesToChange:
                    items[index] = newItem

    def __removeDuplicatePresets(self):
        uniquePresets = OrderedDict()
        seenPresets = set()
        for presetType, items in self.__consumablesPresets.items():
            intCDs = tuple((item.intCD for item in items))
            if intCDs not in seenPresets:
                seenPresets.add(intCDs)
                uniquePresets[presetType] = items

        self.__consumablesPresets = uniquePresets

    def __sortPresets(self):
        self.__consumablesPresets = OrderedDict(((presetType, [ consumables[index] for index in self.__consumablesOrder if index < len(consumables) ]) for presetType, consumables in self.__consumablesPresets.items()))

    def __getConsumable(self, itemTags):
        return first(self.__itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, REQ_CRITERIA.EQUIPMENT.TAGS(itemTags.includedTags, itemTags.excludedTags), nationID=self.vehicle.nationID).values())
