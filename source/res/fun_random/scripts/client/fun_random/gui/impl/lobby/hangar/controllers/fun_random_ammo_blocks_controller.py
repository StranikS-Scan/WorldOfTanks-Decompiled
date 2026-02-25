# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/controllers/fun_random_ammo_blocks_controller.py
from __future__ import absolute_import
import typing
from fun_random.gui.feature.fun_constants import FunCustomShellsSource
from fun_random.gui.feature.models.custom_abilities import FunCustomAbilitySlot
from fun_random.gui.feature.models.custom_shells import FunCustomShellSlot
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from fun_random.gui.impl.gen.view_models.views.lobby.loadout.fun_random_loadout_constants import FunRandomLoadoutConstants
from fun_random.gui.impl.gen.view_models.views.lobby.loadout.shells.fun_random_custom_ability_slot import FunRandomCustomAbilitySlot
from fun_random.gui.impl.gen.view_models.views.lobby.loadout.shells.fun_random_custom_shell_slot import FunRandomCustomShellSlot
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.common.ammunition_panel.ammunition_panel_blocks import BaseBlock
from gui.impl.lobby.tank_setup.ammunition_panel.blocks_controller import HangarAmmunitionBlocksController

class FunRandomCustomBaseBlock(BaseBlock, FunSubModesWatcher):

    def createBlock(self, viewModel):
        super(FunRandomCustomBaseBlock, self).createBlock(viewModel)
        viewModel.setType(self._getSectionName())

    def _getKeySettings(self):
        return [ slot.command for slot in self._getSubModeCustomSlots() ]

    def _getLayout(self):
        return self._getInstalled()

    def _getInstalled(self):
        return self._getSubModeCustomSlots()

    def _getSetupLayout(self):
        pass

    def _getSubModeCustomSlots(self):
        raise NotImplementedError


class FunRandomCustomShellsBlock(FunRandomCustomBaseBlock):

    def _getAmmunitionSlotModel(self):
        return FunRandomCustomShellSlot()

    def _getSectionName(self):
        return FunRandomLoadoutConstants.FUN_RANDOM_CUSTOM_SHELLS

    def _updateSlotWithItem(self, model, idx, slotItem):
        model.setIntCD(slotItem.shell.intCD)
        model.setCount(slotItem.shell.count)
        model.setImageName(slotItem.shell.imageName)
        model.setOriginalIdx(slotItem.originalIndex)
        model.setImageNameOverride(slotItem.imageNameOverride)
        model.setTooltipOverride(slotItem.tooltipOverride)

    @hasDesiredSubMode(defReturn=[])
    def _getSubModeCustomSlots(self):
        result, originalShells = [], self._vehicle.shells.installed
        customShellsConfig = self.getDesiredSubMode().getConfigurationModel().subMode.customShells
        for layout in customShellsConfig.layouts:
            if layout.shellSource == FunCustomShellsSource.CUSTOM:
                result.append(FunCustomShellSlot.fromCustomLayoutConfig(customShellsConfig, layout))
            if 0 <= layout.shellIndex < len(originalShells) and originalShells[layout.shellIndex]:
                originalShell = originalShells[layout.shellIndex]
                result.append(FunCustomShellSlot.fromShellItem(customShellsConfig, layout, originalShell))

        return result


class FunRandomCustomAbilitiesBlock(FunRandomCustomBaseBlock):

    def _getAmmunitionSlotModel(self):
        return FunRandomCustomAbilitySlot()

    def _getSectionName(self):
        return FunRandomLoadoutConstants.FUN_RANDOM_CUSTOM_ABILITIES

    def _updateSlotWithItem(self, model, idx, slotItem):
        model.setIntCD(slotItem.ability.intCD)
        model.setImageName(slotItem.ability.imageName)
        model.setTooltipAlias(slotItem.tooltipAlias)

    @hasDesiredSubMode(defReturn=[])
    def _getSubModeCustomSlots(self):
        customAbilitiesConfig = self.getDesiredSubMode().getConfigurationModel().subMode.customAbilities
        return [ FunCustomAbilitySlot.fromCustomLayoutConfig(customAbilitiesConfig, layout) for layout in customAbilitiesConfig.layouts ]


class FunRandomHangarAmmunitionBlocksController(HangarAmmunitionBlocksController):

    @tabUpdateFunc(FunRandomLoadoutConstants.FUN_RANDOM_CUSTOM_SHELLS)
    def _updateFunRandomCustomShells(self, viewModel, isFirst=False):
        FunRandomCustomShellsBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(FunRandomLoadoutConstants.FUN_RANDOM_CUSTOM_ABILITIES)
    def _updateFunRandomCustomAbilities(self, viewModel, isFirst=False):
        FunRandomCustomAbilitiesBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)
