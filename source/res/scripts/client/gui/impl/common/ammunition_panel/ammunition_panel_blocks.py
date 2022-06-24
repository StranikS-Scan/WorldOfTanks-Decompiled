# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/ammunition_panel/ammunition_panel_blocks.py
import typing
from account_helpers.settings_core.options import KeyboardSetting
from constants import PLAYER_RANK
from frameworks.wulf import Array
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.battle_ability_ammunition_slot import BattleAbilityAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.opt_device_ammunition_slot import OptDeviceAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.shell_ammunition_slot import ShellAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specialization_model import SpecializationModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.tank_setup_helper import getCategoriesMask, NONE_ID
from helpers import dependency
from helpers.epic_game import searchRankForSlot
from items.components.supply_slot_categories import SlotCategories
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle
EMPTY_NAME = 'empty'

class BaseBlock(object):

    def __init__(self, vehicle, currentSection, ctx=None):
        self._currentSection = currentSection
        self._vehicle = vehicle
        self._ctx = ctx

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
        for idx in range(len(self._getInstalled())):
            slot = self._createAmmunitionSlot(idx)
            self._updateAmmunitionSlot(slot, idx)
            array.addViewModel(slot)

        return array

    def _updateSlots(self, viewModel):
        slots = viewModel.getSlots()
        for idx in range(len(self._getInstalled())):
            slotModel = slots[idx]
            self._updateAmmunitionSlot(slotModel, idx)

        slots.invalidate()

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

    def _getSetupLayout(self):
        raise NotImplementedError

    def _getAmmunitionSlotModel(self):
        return BaseAmmunitionSlot()

    def _createAmmunitionSlot(self, idx):
        slot = self._getAmmunitionSlotModel()
        slot.setId(idx)
        return slot

    def _updateAmmunitionSlot(self, model, idx):
        slotItem = self._getSectionLayout()[idx]
        if slotItem is None:
            self._updateEmptySlot(model, idx)
        else:
            self._updateSlotWithItem(model, idx, slotItem)
        self.__updateSlotKeyName(model, idx)
        return

    def _updateEmptySlot(self, model, idx):
        model.setImageSource(R.images.gui.maps.icons.tanksetup.panel.empty())
        model.setOverlayType(ItemHighlightTypes.EMPTY)
        model.setHighlightType(ItemHighlightTypes.EMPTY)
        model.setIsInstalled(True)
        model.setWithAttention(False)
        model.setItemInstalledSetupIdx(NONE_ID)
        model.setIsMountedMoreThanOne(False)
        model.setIntCD(NONE_ID)

    def _updateSlotWithItem(self, model, idx, slotItem):
        model.setIsInstalled(slotItem in self._getInstalled())
        model.setItemInstalledSetupIdx(self._getSetupLayout().layoutIndex)
        if self._vehicle.isPostProgressionExists:
            installedCount = self._getSetupLayout().getIntCDs().count(slotItem.intCD)
        else:
            installedCount = self._getInstalled().getIntCDs().count(slotItem.intCD)
        model.setIsMountedMoreThanOne(installedCount > 1)
        model.setIntCD(slotItem.intCD)

    def __updateSlotKeyName(self, model, idx):
        keySettings = self._getKeySettings()
        if idx < len(keySettings):
            model.setKeyName(KeyboardSetting(keySettings[idx]).getKeyName())


class OptDeviceBlock(BaseBlock):

    def __init__(self, vehicle, currentSection, ctx=None):
        super(OptDeviceBlock, self).__init__(vehicle, currentSection, ctx)
        self._isSpecializationClickable = ctx.get('specializationClickable', False) if ctx else False

    def createBlock(self, viewModel):
        super(OptDeviceBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def _getSectionName(self):
        return TankSetupConstants.OPT_DEVICES

    def _getAmmunitionSlotModel(self):
        return OptDeviceAmmunitionSlot()

    def _getInstalled(self):
        return self._vehicle.optDevices.installed

    def _getSetupLayout(self):
        return self._vehicle.optDevices.setupLayouts

    def _getLayout(self):
        return self._vehicle.optDevices.layout

    def _updateEmptySlot(self, model, idx):
        super(OptDeviceBlock, self)._updateEmptySlot(model, idx)
        self._updateSpecializations(model, slotItem=None, idx=idx)
        model.setIsIncompatible(False)
        return

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(OptDeviceBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setImageSource(R.images.gui.maps.icons.artefact.dyn(slotItem.descriptor.iconName)())
        self._updateOverlayAspects(model, slotItem)
        self._updateSpecializations(model, slotItem, idx)

    def _updateSpecializations(self, slotModel, slotItem, idx):
        optDeviceItem, isDynamic = self._getSlot(idx)
        slotModel.specializations.setIsDynamic(isDynamic)
        itemCategories = set() if slotItem is None else slotItem.descriptor.categories
        slotModel.setActiveSpecsMask(getCategoriesMask(itemCategories & optDeviceItem.categories))
        isSpecializationClickable = isDynamic and optDeviceItem.categories and self._isSpecializationClickable and self._vehicle.isRoleSlotActive
        specializations = slotModel.specializations.getSpecializations()
        categories = optDeviceItem.categories
        if len(specializations) != len(categories):
            specializations.clear()
            for category in categories:
                specialization = SpecializationModel()
                specialization.setName(category)
                specialization.setIsClickable(isSpecializationClickable)
                specialization.setIsCorrect(category in itemCategories)
                specializations.addViewModel(specialization)

        else:
            for categoryIdx, category in enumerate(categories):
                specialization = specializations[categoryIdx]
                specialization.setName(category)
                specialization.setIsClickable(isSpecializationClickable)
                specialization.setIsCorrect(category in itemCategories)

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

    def _getSlot(self, idx):
        return self._vehicle.optDevices.getSlot(idx)


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

    def _getSetupLayout(self):
        return self._vehicle.shells.setupLayouts

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

    def _getSetupLayout(self):
        return self._vehicle.consumables.setupLayouts

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

    def _getSetupLayout(self):
        return self._vehicle.battleBoosters.setupLayouts

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
    _RANK = 'list_rank_{}'
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def createBlock(self, viewModel):
        super(BattleAbilitiesBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())
        vehType = self._vehicle.type.replace('-', '_')
        viewModel.setVehicle(backport.text(R.strings.menu.classes.short.dyn(vehType)()))
        viewModel.setVehicleType(vehType)

    def _getSectionName(self):
        return TankSetupConstants.BATTLE_ABILITIES

    def _getKeySettings(self):
        pass

    def _getAmmunitionSlotModel(self):
        return BattleAbilityAmmunitionSlot()

    def _getInstalled(self):
        return self._vehicle.battleAbilities.installed

    def _getSetupLayout(self):
        return self._vehicle.battleAbilities.setupLayouts

    def _getLayout(self):
        return self._vehicle.battleAbilities.layout

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(BattleAbilitiesBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setImageSource(R.images.gui.maps.icons.epicBattles.skills.c_48x48.dyn(slotItem.descriptor.iconName)())
        categoryName = self._getSlotCategoryName(idx)
        if categoryName:
            model.setCategoryImgSource(R.images.gui.maps.icons.tanksetup.panel.dyn(categoryName)())
        model.setIsInstalled(slotItem in self._getInstalled())
        self._setRankIcon(model, idx)

    def _setRankIcon(self, model, idx):
        model.setRank(R.invalid())
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        currentRank = None
        if playerDataComp is not None:
            currentRank = playerDataComp.playerRank - 1 if playerDataComp.playerRank is not None else 0
        unlockSlotOrder = self.__epicMetaGameCtrl.getAbilitySlotsUnlockOrder(self._vehicle.descriptor.type)
        slotRank = searchRankForSlot(idx, unlockSlotOrder)
        if slotRank and (currentRank is None or currentRank < slotRank):
            slotRank += 1
            resource = R.images.gui.maps.icons.library.epicRank.dyn(self._RANK.format(PLAYER_RANK.NAMES[slotRank]))()
            model.setRank(resource)
        return

    def _getSlotCategoryName(self, idx):
        slots = self._vehicle.battleAbilities.slots
        slotsOrder = self.__epicMetaGameCtrl.getAbilitySlotsOrder(self._vehicle.descriptor.type)
        if idx >= len(slots):
            return None
        else:
            sID = slotsOrder[idx]
            for slot in slots:
                if sID != slot.slotID:
                    continue
                categories = SlotCategories.ALL
                slotCategory = tuple(categories.intersection(slot.tags))
                if slotCategory:
                    return slotCategory[0]
                return None

            return None
