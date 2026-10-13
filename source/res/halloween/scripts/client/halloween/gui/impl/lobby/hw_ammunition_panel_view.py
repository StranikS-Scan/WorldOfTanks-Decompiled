# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/hw_ammunition_panel_view.py
from __future__ import absolute_import
from itertools import cycle
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController, GroupData
from gui.impl.common.ammunition_panel.ammunition_blocks_controller import BaseAmmunitionBlocksController
from gui.impl.common.ammunition_panel.ammunition_panel_blocks import ConsumablesBlock, ShellsBlock
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_shells_section import AmmunitionShellsSection
from halloween.gui.impl.lobby.tank_setup import HWTankSetupConstants
from halloween.gui.halloween_gui_constants import AmmoPanelSwitchPreset
from halloween.gui.halloween_account_settings import getSettings, AccountSettingsKeys, setSettings
AMMO_SECTIONS_DEFAULT = (TankSetupConstants.SHELLS, HWTankSetupConstants.HW_CONSUMABLES)
AMMO_SECTIONS_ALTERNATIVE = (HWTankSetupConstants.HW_CONSUMABLES, TankSetupConstants.SHELLS)
_PRESET_AMMO_SECTIONS = {AmmoPanelSwitchPreset.PRESET_1: AMMO_SECTIONS_DEFAULT,
 AmmoPanelSwitchPreset.PRESET_2: AMMO_SECTIONS_ALTERNATIVE,
 'default': AMMO_SECTIONS_DEFAULT}
_CMD_KEYS_123 = ('CMD_AMMO_CHOICE_1', 'CMD_AMMO_CHOICE_2', 'CMD_AMMO_CHOICE_3')
_CMD_KEYS_456 = ('CMD_AMMO_CHOICE_4', 'CMD_AMMO_CHOICE_5', 'CMD_AMMO_CHOICE_6')
_CMD_ACCELERATION_ABILITY_KEY = 'CMD_CM_VEHICLE_SWITCH_AUTOROTATION'
_PRESET_MAP_AMMO_KEYS = {AmmoPanelSwitchPreset.PRESET_1: (_CMD_KEYS_123, _CMD_KEYS_456),
 AmmoPanelSwitchPreset.PRESET_2: (_CMD_KEYS_456, _CMD_KEYS_123),
 'default': (_CMD_KEYS_123, _CMD_KEYS_456)}

class HWConsumablesBlock(ConsumablesBlock):

    def _getSectionName(self):
        return HWTankSetupConstants.HW_CONSUMABLES

    def _getKeySettings(self):
        return _PRESET_MAP_AMMO_KEYS.get(getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET), 'default')[1]


class HWShellsBlock(ShellsBlock):

    def _getKeySettings(self):
        return _PRESET_MAP_AMMO_KEYS.get(getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET), 'default')[0]


class HWAmmunitionBlocksController(BaseAmmunitionBlocksController):

    @tabUpdateFunc(TankSetupConstants.SHELLS)
    def _updateShells(self, viewModel, isFirst=False):
        HWShellsBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(HWTankSetupConstants.HW_CONSUMABLES)
    def _updateHWConsumables(self, viewModel, isFirst=False):
        HWConsumablesBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    def _createViewModel(self, name):
        return AmmunitionShellsSection() if name == TankSetupConstants.SHELLS else AmmunitionItemsSection()


class HWHangarAmmunitionGroupsController(AmmunitionGroupsController):
    __slots__ = ('_presetCycle',)
    _guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, vehicle, autoCreating=True, ctx=None):
        super(HWHangarAmmunitionGroupsController, self).__init__(vehicle, autoCreating=autoCreating, ctx=ctx)
        self._presetCycle = cycle(AmmoPanelSwitchPreset.ALL)

    def finalize(self):
        super(HWHangarAmmunitionGroupsController, self).finalize()
        self._presetCycle = None
        return

    def setNextPreset(self, viewModel=None):
        currentPreset = self._getPreset()
        nextPreset = next((preset for preset in self._presetCycle if preset != currentPreset), AmmoPanelSwitchPreset.PRESET_1)
        self._setPreset(nextPreset)
        if viewModel:
            self.createGroupsModels(viewModel.getGroups())

    def _getGroups(self):
        if self._vehicle is None:
            return []
        else:
            ammoSections = _PRESET_AMMO_SECTIONS.get(self._getPreset(), 'default')
            groups = (GroupData(AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS, ammoSections),)
            return groups

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return HWAmmunitionBlocksController(vehicle, ctx=ctx)

    @staticmethod
    def _setPreset(presetNum):
        setSettings(AccountSettingsKeys.AMMO_PANEL_PRESET, presetNum)

    @staticmethod
    def _getPreset():
        return getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET)
