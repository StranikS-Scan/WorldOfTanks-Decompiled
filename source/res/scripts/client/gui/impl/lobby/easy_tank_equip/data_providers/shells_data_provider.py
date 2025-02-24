# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/data_providers/shells_data_provider.py
from collections import OrderedDict
from copy import copy
from typing import TYPE_CHECKING
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import EasyTankEquip
from gui.easy_tank_equip.easy_tank_equip_helpers import getEasyTankEquipSetting, setEasyTankEquipSetting
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.shells_preset_model import ShellsPresetType
from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider, PresetInfo, SlotInfo
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
from helpers import dependency
from skeletons.gui.game_control import IEasyTankEquipController
if TYPE_CHECKING:
    from typing import List, Optional, Dict
    from gui.shared.gui_items.vehicle_modules import Shell

class ShellsPresetSlotInfo(object):

    def __init__(self, shell, info, slotIdx):
        self.shell = shell
        self.slotIdx = slotIdx
        self.info = info


class ShellsPresetInfo(PresetInfo):

    def __init__(self, installed, storedItemsCount, installedItemsCount, itemPrice, presetType, items):
        super(ShellsPresetInfo, self).__init__(installed, storedItemsCount, installedItemsCount, itemPrice)
        self.presetType = presetType
        self.items = items


class ShellsDataProvider(BaseDataProvider):
    __easyTankEquipCtrl = dependency.descriptor(IEasyTankEquipController)

    def __init__(self, vehicle, balance):
        super(ShellsDataProvider, self).__init__(vehicle, balance)
        self.__installedShells = self.vehicle.shells.installed.getItems()
        self.__shellsPresets = OrderedDict()

    def initialize(self):
        super(ShellsDataProvider, self).initialize()
        if not self.__shellsPresets:
            return
        defaultPresetIndex = min(getEasyTankEquipSetting(EasyTankEquip.SHELLS_CARD_SELECTED_PRESET_INDEX), len(self.presets) - 1)
        self.currentPresetIndex, currentPreset = self._getCurrentPresetInfo(defaultPresetIndex)
        self.isProposalSelected = sum((shell.count for shell in self.__installedShells)) < self.vehicle.ammoMaxSize and not (self.lastCheckedBalance.getShortage(currentPreset.itemPrice.price) or self.isCurrentPresetDisabledForApplying())

    def finalize(self):
        self.__installedShells = None
        self.__shellsPresets.clear()
        super(ShellsDataProvider, self).finalize()
        return

    def setValuesFromCurrentPreset(self):
        shells = self.__shellsPresets.values()[self.currentPresetIndex]
        self.vehicle.shells.setLayout(*shells)
        self.vehicle.shells.setInstalled(*shells)

    def revertChangesFromSelectedPreset(self):
        self.vehicle.shells.setLayout(*self.__installedShells)
        self.vehicle.shells.setInstalled(*self.__installedShells)

    def getPresets(self):
        self.__setShellsPresets()
        return self.__getPresetsInfo()

    def updatePresets(self, fullUpdate=False):
        presets = self.getPresets() if fullUpdate else self.__getPresetsInfo()
        self.presets = presets
        presetIndex = min(self.currentPresetIndex, len(presets) - 1)
        self.currentPresetIndex = presetIndex

    def swapSlots(self, firstSlot, secondSlot):
        presetItems = self.__shellsPresets.values()[self.currentPresetIndex]
        presetItems[firstSlot], presetItems[secondSlot] = presetItems[secondSlot], presetItems[firstSlot]
        self.presets = self.__getPresetsInfo()

    def getCurrentPresetItemsIds(self):
        if self.isProposalDisabled():
            return []
        return [ shell.intCD for shell in self.__shellsPresets.values()[self.currentPresetIndex] ]

    def saveAccountSettings(self):
        setEasyTankEquipSetting(EasyTankEquip.SHELLS_CARD_SELECTED_PRESET_INDEX, self.currentPresetIndex)

    def _getPresetDataForApplying(self):
        data = super(ShellsDataProvider, self)._getPresetDataForApplying()
        data.update({'shells': self.__shellsPresets.values()[self.currentPresetIndex]})
        return data

    def __getPresetsInfo(self):
        return [ self.__getShellsPresetInfo(presetType, items) for presetType, items in self.__shellsPresets.items() ]

    def __getShellsPresetInfo(self, presetType, shells):
        presetItems = self.__getShellsPresetItems(shells)
        storedItemsCount = len([ item for item in presetItems if item.info.storedItemsCount > 0 ])
        installedItemsCount = len([ item for item in presetItems if item.info.installedItemsCount > 0 ])
        itemPrice = sum([ item.info.itemPrice for item in presetItems ], ITEM_PRICE_ZERO)
        return ShellsPresetInfo(installed=self.__isShellsPresetInstalled(shells), storedItemsCount=storedItemsCount, installedItemsCount=installedItemsCount, itemPrice=itemPrice, presetType=presetType, items=presetItems)

    def __getShellsPresetItems(self, shells):
        return [ ShellsPresetSlotInfo(shell=shell, info=self.__getSlotInfo(shell), slotIdx=slotIdx) for slotIdx, shell in enumerate(shells) ]

    def __getSlotInfo(self, shell):
        shellOnVehicleCount = max((item.count for item in self.vehicle.shells.setupLayouts if item == shell))
        shellInventoryCount = shell.inventoryCount
        shellAvailableCount = shellInventoryCount + shellOnVehicleCount
        isOnVehicle = 0 < shell.count <= shellOnVehicleCount
        needToBuyCount = max(shell.count - shellAvailableCount, 0)
        isInStorage = not isOnVehicle and needToBuyCount == 0 and shell.count > 0
        itemPrice = shell.getBuyPrice() * needToBuyCount
        return SlotInfo(storedItemsCount=int(isInStorage), installedItemsCount=int(isOnVehicle), itemPrice=itemPrice)

    def __isShellsPresetInstalled(self, shells):
        preset = {(shell.intCD, shell.count) for shell in shells}
        installed = {(shell.intCD, shell.count) for shell in self.__installedShells}
        return preset == installed

    def __getAdvancedShells(self, shells):
        if len(shells) <= 1 or shells[1].count != 0:
            return None
        else:
            diff = int(round(shells[0].count * self.__easyTankEquipCtrl.config.ammunitionReductionFactor))
            if diff == 0:
                return None
            advancedShells = [ copy(shell) for shell in shells ]
            advancedShells[0].count -= diff
            advancedShells[1].count += diff
            return self.__sortPresetByAnother(advancedShells, self.__installedShells)

    @staticmethod
    def __sortPresetByAnother(shells, sampleShells):
        shellsMap = {shell.intCD:shell for shell in shells}
        return [ shellsMap[sampleShell.intCD] for sampleShell in sampleShells ]

    def __setShellsPresets(self):
        self.__shellsPresets.clear()
        gunDefaultAmmo = g_currentVehicle.item.gun.defaultAmmo
        defaultShells = self.__sortPresetByAnother(gunDefaultAmmo, self.__installedShells)
        self.__shellsPresets[ShellsPresetType.STANDARD] = defaultShells
        advancedShells = self.__getAdvancedShells(gunDefaultAmmo)
        if advancedShells:
            self.__shellsPresets[ShellsPresetType.ADVANCED] = advancedShells
