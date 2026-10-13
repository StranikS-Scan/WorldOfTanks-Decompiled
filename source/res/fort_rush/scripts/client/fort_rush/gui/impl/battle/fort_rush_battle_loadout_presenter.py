# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/fort_rush_battle_loadout_presenter.py
from __future__ import absolute_import
import json
import logging
from typing import List, Callable, Optional
import BigWorld
from Vehicle import Vehicle
from gui.battle_control import avatar_getter
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.loadout.consumables.consumables_model import ConsumablesModel
from gui.impl.gen.view_models.views.lobby.loadout.equipments.equipments_model import EquipmentsModel
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.ammunition_panel_model import AmmunitionPanelModel
from gui.impl.gen.view_models.views.lobby.loadout.shells.shell_model import ShellModel
from gui.impl.gen.view_models.views.lobby.loadout.shells.shells_model import ShellsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_group import AmmunitionItemsGroup
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_setup_selector import SetupStates
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.opt_device_ammunition_slot import OptDeviceAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.shell_ammunition_slot import ShellAmmunitionSlot
from gui.impl.gen.view_models.views.lobby.tank_setup.common.specialization_model import SpecializationModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.consumable_slot_model import ConsumableSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.opt_device_slot_model import OptDeviceSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.pub.view_component import ViewComponent
from gui.shared.gui_items.artefacts import Equipment, OptionalDevice
from gui.shared.gui_items.vehicle_equipment import _EquipmentsSetupGroups
from helpers import dependency
from post_progression_common import TankSetupGroupsId
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_GROUP_ID_EQUIPMENT_AND_SHELLS = TankSetupGroupsId.EQUIPMENT_AND_SHELLS
_GROUP_ID_OPT_DEVICES = TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS

def _computeSetupStates(vehicle, totalSetups):
    return [ (SetupStates.NORMAL if vehicle.isAmmoFullInSetups(layoutIdx) else SetupStates.WARNING) for layoutIdx in range(totalSetups) ]


class FortRushBattleLoadoutPresenter(ViewComponent):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleItem):
        super(FortRushBattleLoadoutPresenter, self).__init__(model=AmmunitionPanelModel)
        self._vehicleItem = vehicleItem
        self._onSwitchCallback = None
        return

    def updateVehicle(self, vehicleItem):
        self._vehicleItem = vehicleItem
        self._updateModel()
        self._updateChildrenVehicle(vehicleItem)

    def _updateChildrenVehicle(self, vehicleItem):
        for _, child in self._childrenByUid.items():
            if hasattr(child, 'updateVehicle'):
                child.updateVehicle(vehicleItem)

    def setOnSwitchCallback(self, callback):
        self._onSwitchCallback = callback

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Consumables(): lambda : _FortRushBattleConsumablesPresenter(self._vehicleItem),
         hangar.Shells(): lambda : _FortRushBattleShellsPresenter(self._vehicleItem),
         hangar.Equipments(): lambda : _FortRushBattleEquipmentsPresenter(self._vehicleItem)}

    def _onLoading(self, *args, **kwargs):
        super(FortRushBattleLoadoutPresenter, self)._onLoading(*args, **kwargs)
        self.viewModel.onChangeSetupIndex += self._onChangeSetupIndex
        self._updateModel()

    def _finalize(self):
        self.viewModel.onChangeSetupIndex -= self._onChangeSetupIndex
        self._onSwitchCallback = None
        super(FortRushBattleLoadoutPresenter, self)._finalize()
        return

    def _onChangeSetupIndex(self, args):
        parsed = json.loads(args.get('args', '{}'))
        groupId = parsed.get('groupId')
        newIndex = parsed.get('currentIndex')
        _logger.debug('[FORT_RUSH][LOADOUT] Switch requested: groupId=%s newIndex=%s', groupId, newIndex)
        if self._onSwitchCallback is not None:
            self._onSwitchCallback(groupId, newIndex)
        return

    def _getGroupCapacity(self, setupLayouts, groupId):
        return setupLayouts.getGroupCapacity(groupId) if setupLayouts else 1

    def _getLayoutIndex(self, setupLayouts, groupId):
        return setupLayouts.getLayoutIndex(groupId) if setupLayouts else 0

    def _createSection(self, sectionType):
        section = AmmunitionItemsSection()
        section.setType(sectionType)
        section.setName(sectionType)
        section.setVehicle(self._vehicleItem.shortUserName)
        section.setVehicleType(self._vehicleItem.type)
        return section

    def _setupSlotBasics(self, slot, idx, item):
        slot.setId(idx)
        slot.setOverlayType(ItemHighlightTypes.EMPTY)
        if item is not None:
            slot.setIntCD(item.intCD)
            slot.setImageName(item.descriptor.iconName)
            slot.setIsInstalled(True)
            return True
        else:
            slot.setIsInstalled(False)
            return False

    def _setGroupSections(self, group, sections):
        groupSections = group.getSections()
        groupSections.clear()
        for section in sections:
            groupSections.addViewModel(section)

        groupSections.invalidate()

    def _setSelector(self, group, groupId, totalSetups, applySetupStates=False):
        selector = group.setupSelector
        battleVehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        isSwitchEnabled = battleVehicle is not None and groupId not in battleVehicle.disabledSwitches
        selector.setIsSwitchEnabled(totalSetups > 1 and isSwitchEnabled)
        selector.setIsPrebattleSwitchDisabled(False)
        if applySetupStates:
            setupStates = _computeSetupStates(self._vehicleItem, totalSetups)
        else:
            setupStates = [SetupStates.NORMAL] * totalSetups
        states = selector.getStates()
        states.clear()
        for state in setupStates:
            states.addNumber(state)

        states.invalidate()
        return

    def _createAmmunitionGroup(self, groupId, setupIdx, totalSetups, applySetupStates=False):
        group = AmmunitionItemsGroup()
        group.setGroupId(groupId)
        group.setCurrentIndex(setupIdx)
        group.setTotalCount(totalSetups)
        self._setSelector(group, groupId, totalSetups, applySetupStates)
        return group

    def _buildShellsAndConsumablesGroup(self, setupLayouts):
        totalSetups = self._getGroupCapacity(setupLayouts, _GROUP_ID_EQUIPMENT_AND_SHELLS)
        currentSetupIdx = self._getLayoutIndex(setupLayouts, _GROUP_ID_EQUIPMENT_AND_SHELLS)
        group = self._createAmmunitionGroup(_GROUP_ID_EQUIPMENT_AND_SHELLS, currentSetupIdx, totalSetups, applySetupStates=True)
        shellsSection = self._buildShellsSection()
        consumablesSection = self._buildConsumablesSection()
        self._setGroupSections(group, [shellsSection, consumablesSection])
        return group

    def _buildOptDevicesAndBoostersGroup(self, setupLayouts):
        totalSetups = self._getGroupCapacity(setupLayouts, _GROUP_ID_OPT_DEVICES)
        currentSetupIdx = self._getLayoutIndex(setupLayouts, _GROUP_ID_OPT_DEVICES)
        group = self._createAmmunitionGroup(_GROUP_ID_OPT_DEVICES, currentSetupIdx, totalSetups)
        equipSection = self._buildOptDevicesSection()
        boostersSection = self._buildBoostersSection()
        self._setGroupSections(group, [equipSection, boostersSection])
        return group

    def _buildShellsSection(self):
        section = self._createSection(TankSetupConstants.SHELLS)
        slots = section.getSlots()
        slots.clear()
        for idx, shell in enumerate(self._vehicleItem.shells.installed.getItems(ignoreEmpty=False)):
            slot = ShellAmmunitionSlot()
            if self._setupSlotBasics(slot, idx, shell):
                slot.setCount(shell.count)
            slots.addViewModel(slot)

        slots.invalidate()
        return section

    def _buildConsumablesSection(self):
        section = self._createSection(TankSetupConstants.CONSUMABLES)
        slots = section.getSlots()
        slots.clear()
        for idx, consumable in enumerate(self._vehicleItem.consumables.installed.getItems(ignoreEmpty=False)):
            slot = BaseAmmunitionSlot()
            if self._setupSlotBasics(slot, idx, consumable) and consumable.isBuiltIn:
                slot.setOverlayType(ItemHighlightTypes.BUILT_IN_EQUIPMENT)
            slots.addViewModel(slot)

        slots.invalidate()
        return section

    def _buildOptDevicesSection(self):
        section = self._createSection(TankSetupConstants.OPT_DEVICES)
        slots = section.getSlots()
        slots.clear()
        for idx, device in enumerate(self._vehicleItem.optDevices.installed.getItems(ignoreEmpty=False)):
            slot = OptDeviceAmmunitionSlot()
            if self._setupSlotBasics(slot, idx, device):
                self._setupOptDeviceOverlay(slot, device)
                self._setupOptDeviceSpecializations(slot, idx, device)
            slots.addViewModel(slot)

        slots.invalidate()
        return section

    def _setupOptDeviceOverlay(self, slot, device):
        slot.setLevel(device.level)
        if device.isDeluxe:
            slot.setOverlayType(ItemHighlightTypes.EQUIPMENT_PLUS)
        elif device.isModernized:
            slot.setOverlayType(ItemHighlightTypes.MODERNIZED)
        elif device.isUpgradable:
            slot.setOverlayType(ItemHighlightTypes.TROPHY_BASIC)
        elif device.isUpgraded:
            slot.setOverlayType(ItemHighlightTypes.TROPHY_UPGRADED)

    def _setupOptDeviceSpecializations(self, slot, idx, device):
        optDeviceSlotData, isDynamic = self._vehicleItem.optDevices.getSlot(idx)
        slot.specializations.setIsDynamic(isDynamic)
        specializations = slot.specializations.getSpecializations()
        specializations.clear()
        slotCategories = optDeviceSlotData.categories
        itemCategories = device.descriptor.categories
        for category in slotCategories:
            spec = SpecializationModel()
            spec.setName(category)
            spec.setIsCorrect(category in itemCategories)
            spec.setIsClickable(False)
            specializations.addViewModel(spec)

        specializations.invalidate()

    def _buildBoostersSection(self):
        section = self._createSection(TankSetupConstants.BATTLE_BOOSTERS)
        slots = section.getSlots()
        slots.clear()
        for idx, booster in enumerate(self._vehicleItem.battleBoosters.installed.getItems(ignoreEmpty=False)):
            slot = BaseAmmunitionSlot()
            if self._setupSlotBasics(slot, idx, booster):
                self._setupBoosterOverlay(slot, booster)
            slots.addViewModel(slot)

        slots.invalidate()
        return section

    def _setupBoosterOverlay(self, slot, booster):
        isPerkReplace = booster.isCrewBooster() and not booster.isAffectedSkillLearnt(self._vehicleItem) and not booster.isBuiltinPerkBooster()
        if isPerkReplace:
            slot.setOverlayType(ItemHighlightTypes.BATTLE_BOOSTER_REPLACE)
        else:
            slot.setOverlayType(ItemHighlightTypes.BATTLE_BOOSTER)

    def _updateModel(self):
        if self._vehicleItem is None:
            return
        else:
            with self.viewModel.transaction() as model:
                model.setVehicleId(str(self._vehicleItem.intCD))
                model.setIsDisabled(False)
                model.setSelectedSlot(AmmunitionPanelModel.NO_SLOT_SELECTED)
                groups = model.getGroups()
                groups.clear()
                setupLayouts = self._vehicleItem.setupLayouts
                shellsGroup = self._buildShellsAndConsumablesGroup(setupLayouts)
                groups.addViewModel(shellsGroup)
                equipGroup = self._buildOptDevicesAndBoostersGroup(setupLayouts)
                groups.addViewModel(equipGroup)
                groups.invalidate()
            return


class _FortRushBattleConsumablesPresenter(ViewComponent):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleItem):
        super(_FortRushBattleConsumablesPresenter, self).__init__(model=ConsumablesModel)
        self._vehicleItem = vehicleItem

    def updateVehicle(self, vehicleItem):
        self._vehicleItem = vehicleItem
        self._updateModel()

    def _onLoading(self, *args, **kwargs):
        super(_FortRushBattleConsumablesPresenter, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        if self._vehicleItem is None:
            return
        else:
            with self.getViewModel().transaction() as model:
                model.setHasChanges(False)
                model.setAutoloadEnabled(False)
                consumables = model.getConsumables()
                consumables.clear()
                for idx, item in enumerate(self._vehicleItem.consumables.installed.getItems(ignoreEmpty=False)):
                    slot = ConsumableSlotModel()
                    slot.setInstalledSlotId(idx)
                    if item is not None:
                        slot.setIntCD(item.intCD)
                        slot.setImageName(item.descriptor.iconName)
                        slot.setItemName(item.userName)
                        slot.setIsMounted(True)
                    else:
                        slot.setIsMounted(False)
                    consumables.addViewModel(slot)

                consumables.invalidate()
            return


class _FortRushBattleShellsPresenter(ViewComponent):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleItem):
        super(_FortRushBattleShellsPresenter, self).__init__(model=ShellsModel)
        self._vehicleItem = vehicleItem

    def updateVehicle(self, vehicleItem):
        self._vehicleItem = vehicleItem
        self._updateModel()

    def _onLoading(self, *args, **kwargs):
        super(_FortRushBattleShellsPresenter, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        if self._vehicleItem is None:
            return
        else:
            with self.getViewModel().transaction() as model:
                model.setHasChanges(False)
                model.setAutoloadEnabled(False)
                shells = model.getShells()
                shells.clear()
                for _, item in enumerate(self._vehicleItem.shells.installed.getItems(ignoreEmpty=False)):
                    shell = ShellModel()
                    if item is not None:
                        shell.setIntCD(item.intCD)
                        shell.setCount(item.count)
                        shell.setType(item.type)
                        shell.setKind(item.descriptor.kind)
                        shell.setIsMounted(True)
                    shells.addViewModel(shell)

                shells.invalidate()
            return


class _FortRushBattleEquipmentsPresenter(ViewComponent):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleItem):
        super(_FortRushBattleEquipmentsPresenter, self).__init__(model=EquipmentsModel)
        self._vehicleItem = vehicleItem

    def updateVehicle(self, vehicleItem):
        self._vehicleItem = vehicleItem
        self._updateModel()

    def _onLoading(self, *args, **kwargs):
        super(_FortRushBattleEquipmentsPresenter, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        if self._vehicleItem is None:
            return
        else:
            with self.getViewModel().transaction() as model:
                model.setHasChanges(False)
                equipments = model.getSimpleEquipments()
                equipments.clear()
                for idx, item in enumerate(self._vehicleItem.optDevices.installed.getItems(ignoreEmpty=False)):
                    slot = OptDeviceSlotModel()
                    slot.setInstalledSlotId(idx)
                    if item is not None:
                        slot.setIntCD(item.intCD)
                        slot.setImageName(item.descriptor.iconName)
                        slot.setIsMounted(True)
                    else:
                        slot.setIsMounted(False)
                    equipments.addViewModel(slot)

                equipments.invalidate()
            return
