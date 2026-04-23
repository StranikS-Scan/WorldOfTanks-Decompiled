# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/hangar_ammunition_panel_view.py
from __future__ import absolute_import
from itertools import cycle
from helpers import dependency
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController, GroupData
from gui.impl.common.ammunition_panel.ammunition_blocks_controller import BaseAmmunitionBlocksController
from gui.impl.common.ammunition_panel.ammunition_panel_blocks import ConsumablesBlock, ShellsBlock, OptDeviceBlock, BattleBoostersBlock
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_shells_section import AmmunitionShellsSection
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants
from last_stand.gui.ls_gui_constants import AmmoPanelSwitchPreset
from last_stand.gui.ls_account_settings import getSettings, AccountSettingsKeys, setSettings
from skeletons.gui.impl import IGuiLoader
from LSAccountEquipmentController import getLSConsumables
LS_GROUPS = (GroupData(AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS, (TankSetupConstants.SHELLS, LSTankSetupConstants.LS_CONSUMABLES)), GroupData(AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS, (TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS)))
LS_GROUPS_ALTERNATIVE = (GroupData(AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS, (LSTankSetupConstants.LS_CONSUMABLES, TankSetupConstants.SHELLS)), GroupData(AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS, (TankSetupConstants.OPT_DEVICES, TankSetupConstants.BATTLE_BOOSTERS)))
_PRESET_AMMO_SECTIONS = {AmmoPanelSwitchPreset.PRESET_1: LS_GROUPS,
 AmmoPanelSwitchPreset.PRESET_2: LS_GROUPS_ALTERNATIVE,
 'default': LS_GROUPS}
_CMD_KEYS_123 = ('CMD_AMMO_CHOICE_1', 'CMD_AMMO_CHOICE_2', 'CMD_AMMO_CHOICE_3')
_CMD_KEYS_456 = ('CMD_AMMO_CHOICE_4', 'CMD_AMMO_CHOICE_5', 'CMD_AMMO_CHOICE_6')
_PRESET_MAP_AMMO_KEYS = {AmmoPanelSwitchPreset.PRESET_1: (_CMD_KEYS_123, _CMD_KEYS_456),
 AmmoPanelSwitchPreset.PRESET_2: (_CMD_KEYS_456, _CMD_KEYS_123),
 'default': (_CMD_KEYS_123, _CMD_KEYS_456)}

class LSConsumablesBlock(ConsumablesBlock):

    def _getSectionName(self):
        return LSTankSetupConstants.LS_CONSUMABLES

    def _getKeySettings(self):
        return _PRESET_MAP_AMMO_KEYS.get(getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET), 'default')[1]

    def _getInstalled(self):
        return getLSConsumables(self._vehicle).installed

    def _getLayout(self):
        return getLSConsumables(self._vehicle).layout


class LSShellsBlock(ShellsBlock):

    def _updateSlotWithItem(self, model, idx, slotItem):
        super(LSShellsBlock, self)._updateSlotWithItem(model, idx, slotItem)
        model.setIsInfinity(not slotItem.descriptor.isForceFinite)

    def _getKeySettings(self):
        return _PRESET_MAP_AMMO_KEYS.get(getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET), 'default')[0]


class LSAmmunitionBlocksController(BaseAmmunitionBlocksController):

    @tabUpdateFunc(TankSetupConstants.SHELLS)
    def _updateShells(self, viewModel, isFirst=False):
        LSShellsBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(LSTankSetupConstants.LS_CONSUMABLES)
    def _updateLSConsumables(self, viewModel, isFirst=False):
        LSConsumablesBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.OPT_DEVICES)
    def _updateOptDevices(self, viewModel, isFirst=False):
        OptDeviceBlock(self._vehicle, self._currentSection, ctx=self._ctx).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.BATTLE_BOOSTERS)
    def _updateBattleBoosters(self, viewModel, isFirst=False):
        BattleBoostersBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    def _createViewModel(self, name):
        return AmmunitionShellsSection() if name == TankSetupConstants.SHELLS else AmmunitionItemsSection()


class LSHangarAmmunitionGroupsController(AmmunitionGroupsController):
    _guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, vehicle, autoCreating=True, ctx=None):
        super(LSHangarAmmunitionGroupsController, self).__init__(vehicle, autoCreating=autoCreating, ctx=ctx)
        self._presetCycle = cycle(AmmoPanelSwitchPreset.ALL)

    def finalize(self):
        super(LSHangarAmmunitionGroupsController, self).finalize()
        self._presetCycle = None
        return

    def setNextPreset(self, viewModel=None):
        currentPreset = self._getPreset()
        nextPreset = next((preset for preset in self._presetCycle if preset != currentPreset), AmmoPanelSwitchPreset.PRESET_1)
        self._setPreset(nextPreset)
        if viewModel:
            self.createGroupsModels(viewModel.getGroups())

    def _getGroups(self):
        return [] if self._vehicle is None else _PRESET_AMMO_SECTIONS.get(self._getPreset(), 'default')

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return LSAmmunitionBlocksController(vehicle, ctx=ctx)

    @staticmethod
    def _setPreset(presetNum):
        setSettings(AccountSettingsKeys.AMMO_PANEL_PRESET, presetNum)

    @staticmethod
    def _getPreset():
        return getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET)
