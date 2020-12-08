# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel_blocks.py
import itertools
import typing
from account_helpers.settings_core.options import KeyboardSetting
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.battle_ability_ammunition_slot import BattleAbilityAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ny_style_ammunition_slot import NyStyleAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.opt_device_ammunition_slot import OptDeviceAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.shell_ammunition_slot import ShellAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specialization_model import SpecializationModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.tank_setup_helper import getCategoriesMask, NONE_ID
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
EMPTY_NAME = 'empty'

class BaseBlock(object):

    def __init__(self, vehicle, currentSection):
        self._currentSection = currentSection
        self._vehicle = vehicle

    def adapt(self, viewModel, isFirst):
        if isFirst:
            self.createBlock(viewModel)
        else:
            self.updateBlock(viewModel)

    def createBlock(self, viewModel):
        self.updateBlock(viewModel)

    def updateBlock(self, viewModel):
        if len(self._getInstalled()) != len(viewModel.getSlots()):
            viewModel.setSlots(self._createSlots())
        else:
            self._updateSlots(viewModel)

    def _createSlots(self):
        array = Array()
        rangeIter = xrange(len(self._getInstalled()))
        for idx, keyCmd in itertools.izip_longest(rangeIter, self._getKeySettings()):
            if idx is None:
                break
            slot = self._createAmmunitionSlot(idx)
            if keyCmd is not None:
                slot.setKeyName(KeyboardSetting(keyCmd).getKeyName())
            self._updateAmmunitionSlot(slot, idx)
            array.addViewModel(slot)

        return array

    def _updateSlots(self, viewModel):
        slots = viewModel.getSlots()
        for idx in xrange(len(self._getInstalled())):
            slotModel = slots[idx]
            self._updateAmmunitionSlot(slotModel, idx)

    def _getSectionName(self):
        raise NotImplementedError

    def _getKeySettings(self):
        pass

    def _getSectionLayout(self):
        return self._getLayout() if self._currentSection == self._getSectionName() else self._getInstalled()

    def _getLayout(self):
        raise NotImplementedError

    def _getInstalled(self):
        raise NotImplementedError

    def _getAmmunitionSlotModel(self):
        return BaseAmmunitionSlot()

    def _createAmmunitionSlot(self, idx):
        slot = self._getAmmunitionSlotModel()
        slot.setId(idx)
        return slot

    def _updateAmmunitionSlot(self, model, idx):
        slotItem = self._getSectionLayout()[idx]
        if self._getSectionLayout()[idx] is None:
            self._updateEmptySlot(model, idx)
        else:
            self._updateSlotWithItem(model, idx, slotItem)
        return

    def _updateEmptySlot(self, model, idx):
        model.setImageSource(R.images.gui.maps.icons.tanksetup.panel.empty())
        model.setOverlayType(ItemHighlightTypes.EMPTY)
        model.setHighlightType(ItemHighlightTypes.EMPTY)
        model.setIsInstalled(True)
        model.setWithAttention(False)
        model.setIntCD(NONE_ID)

    def _updateSlotWithItem(self, model, idx, slotItem):
        model.setIsInstalled(slotItem in self._getInstalled())
        model.setIntCD(slotItem.intCD)


class OptDeviceBlock(BaseBlock):

    def createBlock(self, viewModel):
        super(OptDeviceBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def _getSectionName(self):
        return TankSetupConstants.OPT_DEVICES

    def _getAmmunitionSlotModel(self):
        return OptDeviceAmmunitionSlot()

    def _getInstalled(self):
        return self._vehicle.optDevices.installed

    def _getLayout(self):
        return self._vehicle.optDevices.layout

    def _createAmmunitionSlot(self, idx):
        slot = super(OptDeviceBlock, self)._createAmmunitionSlot(idx)
        specializations = slot.specializations.getSpecializations()
        for category in self._getSlotCategories(idx):
            specialization = SpecializationModel()
            specialization.setName(category)
            specializations.addViewModel(specialization)

        return slot

    def _updateEmptySlot(self, model, idx):
        super(OptDeviceBlock, self)._updateEmptySlot(model, idx)
        self._updateSpecializations(model, slotItem=None, idx=idx)
        model.setIsIncompatible(False)
        return

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(OptDeviceBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setImageSource(R.images.gui.maps.icons.artefact.dyn(slotItem.descriptor.iconName)())
        model.setIsInstalled(slotItem in self._getInstalled())
        self._updateOverlayAspects(model, slotItem)
        self._updateSpecializations(model, slotItem, idx)

    def _updateSpecializations(self, slotModel, slotItem, idx):
        specializations = slotModel.specializations.getSpecializations()
        itemCategories = set() if slotItem is None else slotItem.descriptor.categories
        slotModel.setActiveSpecsMask(getCategoriesMask(itemCategories & self._getSlotCategories(idx)))
        for specialization in specializations:
            isInstalledCorrectly = specialization.getName() in itemCategories
            specialization.setIsCorrect(isInstalledCorrectly)

        specializations.invalidate()
        return

    def _updateOverlayAspects(self, slotModel, slotItem):
        if slotItem.isDeluxe:
            slotModel.setOverlayType(ItemHighlightTypes.EQUIPMENT_PLUS)
        elif slotItem.isUpgradable:
            slotModel.setOverlayType(ItemHighlightTypes.TROPHY_BASIC)
        elif slotItem.isUpgraded:
            slotModel.setOverlayType(ItemHighlightTypes.TROPHY_UPGRADED)
        else:
            slotModel.setOverlayType(ItemHighlightTypes.EMPTY)

    def _getSlotCategories(self, idx):
        return self._vehicle.optDevices.slots[idx].categories


class ShellsBlock(BaseBlock):

    def createBlock(self, viewModel):
        super(ShellsBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def _getSectionName(self):
        return TankSetupConstants.SHELLS

    def _getKeySettings(self):
        pass

    def _getAmmunitionSlotModel(self):
        return ShellAmmunitionSlot()

    def _getInstalled(self):
        return self._vehicle.shells.installed

    def _getLayout(self):
        return self._vehicle.shells.layout

    def _updateSlotWithItem(self, model, idx, slotItem):
        model.setImageSource(R.images.gui.maps.icons.shell.small.dyn(slotItem.descriptor.iconName)())
        model.setCount(slotItem.count)
        model.setIntCD(slotItem.intCD)


class ConsumablesBlock(BaseBlock):

    def createBlock(self, viewModel):
        super(ConsumablesBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def _getSectionName(self):
        return TankSetupConstants.CONSUMABLES

    def _getKeySettings(self):
        pass

    def _getInstalled(self):
        return self._vehicle.consumables.installed

    def _getLayout(self):
        return self._vehicle.consumables.layout

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(ConsumablesBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setImageSource(R.images.gui.maps.icons.artefact.dyn(slotItem.descriptor.iconName)())
        self._updateOverlayAspects(model, slotItem)

    def _updateOverlayAspects(self, slotModel, slotItem):
        if slotItem.isBuiltIn:
            slotModel.setOverlayType(ItemHighlightTypes.BUILT_IN_EQUIPMENT)
        else:
            slotModel.setOverlayType(ItemHighlightTypes.EMPTY)


class BattleBoostersBlock(BaseBlock):

    def createBlock(self, viewModel):
        super(BattleBoostersBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def _getSectionName(self):
        return TankSetupConstants.BATTLE_BOOSTERS

    def _getInstalled(self):
        return self._vehicle.battleBoosters.installed

    def _getLayout(self):
        return self._vehicle.battleBoosters.layout

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(BattleBoostersBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setImageSource(R.images.gui.maps.icons.artefact.dyn(slotItem.descriptor.iconName)())
        self._updateOverlayAspects(model, slotItem)

    def _updateOverlayAspects(self, slotModel, slotItem):
        affectsAtTTC = slotItem.isAffectsOnVehicle(self._vehicle)
        slotModel.setWithAttention(not affectsAtTTC)
        if slotItem.isCrewBooster():
            isPerkReplace = not slotItem.isAffectedSkillLearnt(self._vehicle)
            if isPerkReplace:
                slotModel.setOverlayType(ItemHighlightTypes.BATTLE_BOOSTER_REPLACE)
            else:
                slotModel.setOverlayType(ItemHighlightTypes.BATTLE_BOOSTER)
        else:
            slotModel.setOverlayType(ItemHighlightTypes.BATTLE_BOOSTER)


class BattleAbilitiesBlock(BaseBlock):

    def createBlock(self, viewModel):
        super(BattleAbilitiesBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def _getSectionName(self):
        return TankSetupConstants.BATTLE_ABILITIES

    def _getKeySettings(self):
        pass

    def _getAmmunitionSlotModel(self):
        return BattleAbilityAmmunitionSlot()

    def _getInstalled(self):
        return self._vehicle.battleAbilities.installed

    def _getLayout(self):
        return self._vehicle.battleAbilities.layout

    def _updateEmptySlot(self, model, idx):
        super(BattleAbilitiesBlock, self)._updateEmptySlot(model, idx)
        model.setLevel(0)

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(BattleAbilitiesBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setImageSource(R.images.gui.maps.icons.artefact.dyn(slotItem.descriptor.iconName)())
        model.setLevel(slotItem.level)


class NewYearStyleBlock(BaseBlock):
    _index = 0

    def createBlock(self, viewModel):
        super(NewYearStyleBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def updateBlock(self, viewModel):
        if not viewModel.getSlots():
            viewModel.setSlots(self._createSlots())
        else:
            slot = viewModel.getSlots()[self._index]
            self._updateSlot(slot)

    def _createSlots(self):
        array = Array()
        slot = self._createAmmunitionSlot(self._index)
        self._updateSlot(slot)
        array.addViewModel(slot)
        return array

    def _getSectionName(self):
        return TankSetupConstants.TOGGLE_NY_STYLE

    def _getAmmunitionSlotModel(self):
        return NyStyleAmmunitionSlot()

    def _updateSlot(self, slot):
        vehicle = self._vehicle
        slot.setIsSelected(vehicle.isNewYearOutfitSet())
        slot.setIsLocked(vehicle.isNewYearOutfitChangesLocked())
        slot.setIsOutfitLocked(vehicle.isOutfitLocked)

    def _getLayout(self):
        return None

    def _getInstalled(self):
        return None
