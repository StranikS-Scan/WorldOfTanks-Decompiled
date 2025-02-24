# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/data_providers/base_data_provider.py
from enum import Enum
from typing import TYPE_CHECKING
import Event
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.preset_model import PresetDisableReason
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalDisableReason
from shared_utils import first
from gui.shared.money import ZERO_MONEY
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
if TYPE_CHECKING:
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.money import Money
    from typing import List, Optional, Tuple, Dict

class CardLogStatuses(str, Enum):
    SELECTED = 'selected'
    NOT_SELECTED = 'not_selected'
    DISABLED = 'disabled'
    INSTALLED = 'installed'


class SlotInfo(object):

    def __init__(self, storedItemsCount, installedItemsCount, itemPrice):
        self.storedItemsCount = storedItemsCount
        self.installedItemsCount = installedItemsCount
        self.itemPrice = itemPrice


class PresetInfo(object):

    def __init__(self, installed, storedItemsCount=0, installedItemsCount=0, itemPrice=ITEM_PRICE_ZERO, disableReason=PresetDisableReason.NONE):
        self.installed = installed
        self.storedItemsCount = storedItemsCount
        self.installedItemsCount = installedItemsCount
        self.itemPrice = itemPrice
        self.disableReason = disableReason


class BaseDataProvider(object):

    def __init__(self, vehicle, balance):
        self.vehicle = vehicle
        self.lastCheckedBalance = balance
        self.currentPresetIndex = 0
        self.proposalDisableReason = ProposalDisableReason.NONE
        self.__presets = None
        self.__isProposalSelected = False
        self.__em = Event.EventManager()
        self.onSelect = Event.Event(self.__em)
        self.onSwitchPreset = Event.Event(self.__em)
        self.onPricesUpdated = Event.Event(self.__em)
        self.onPresetsUpdated = Event.Event(self.__em)
        return

    @property
    def presets(self):
        if not self.__presets:
            self.__presets = self.getPresets()
        return self.__presets

    @presets.setter
    def presets(self, value):
        self.__presets = value
        self.applyNewPresetOnVehicle()
        self.onPresetsUpdated()

    @property
    def isProposalSelected(self):
        return self.__isProposalSelected

    @isProposalSelected.setter
    def isProposalSelected(self, value):
        if value != self.__isProposalSelected:
            self.__isProposalSelected = value
            self.selectStatusChanged()

    def initialize(self):
        self.__presets = self.getPresets()

    def finalize(self):
        self.__presets = None
        self.__em.clear()
        return

    def selectProposal(self):
        self.isProposalSelected = not self.isProposalSelected
        self.onSelect()

    def switchPreset(self, presetIndex):
        self.currentPresetIndex = presetIndex
        self.applyNewPresetOnVehicle()
        self.onSwitchPreset()

    def updateBalance(self, balance):
        if self.lastCheckedBalance != balance:
            self.lastCheckedBalance = balance
            self.onPricesUpdated(balance)

    def isCurrentPresetDisableReasonChanged(self):
        return False

    def isCurrentPresetDisabledForApplying(self):
        return self.isCurrentPresetDisabled() or self.presets[self.currentPresetIndex].installed

    def getBalanceRemains(self):
        return (self.lastCheckedBalance - self.getPresetPrice()).toNonNegative() if self.isProposalSelected else self.lastCheckedBalance

    def getPresetPrice(self):
        return self.presets[self.currentPresetIndex].itemPrice.price if self.presets else ZERO_MONEY

    def isProposalDisabled(self):
        return self.proposalDisableReason != ProposalDisableReason.NONE

    def isCurrentPresetDisabled(self):
        currentPreset = self.presets[self.currentPresetIndex]
        return currentPreset.disableReason != PresetDisableReason.NONE

    def getCardLogStatus(self):
        if self.isProposalDisabled() or self.isCurrentPresetDisabled():
            return CardLogStatuses.DISABLED
        if self.presets[self.currentPresetIndex].installed:
            return CardLogStatuses.INSTALLED
        return CardLogStatuses.SELECTED if self.isProposalSelected else CardLogStatuses.NOT_SELECTED

    def applyNewPresetOnVehicle(self):
        if self.isProposalSelected:
            if self.isCurrentPresetDisabledForApplying():
                self.revertChangesFromSelectedPreset()
            else:
                self.setValuesFromCurrentPreset()

    def selectStatusChanged(self):
        if self.isProposalSelected:
            self.setValuesFromCurrentPreset()
        else:
            self.revertChangesFromSelectedPreset()

    def getPresetDataForApplying(self):
        return None if not self.isProposalSelected or self.isCurrentPresetDisabledForApplying() else self._getPresetDataForApplying()

    def saveAccountSettings(self):
        pass

    def getPresets(self):
        raise NotImplementedError

    def updatePresets(self, fullUpdate=False):
        raise NotImplementedError

    def getCurrentPresetItemsIds(self):
        raise NotImplementedError

    def setValuesFromCurrentPreset(self):
        raise NotImplementedError

    def revertChangesFromSelectedPreset(self):
        raise NotImplementedError

    def swapSlots(self, firstSlot, secondSlot):
        raise NotImplementedError

    def _getPresetDataForApplying(self):
        return {'price': self.getPresetPrice()}

    def _getCurrentPresetInfo(self, defaultIndex):
        return first(((index, preset) for index, preset in enumerate(self.presets) if preset.installed), default=(defaultIndex, self.presets[defaultIndex]))
