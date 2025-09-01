# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/hangar_ammunition_panel_view.py
from itertools import cycle
from helpers import dependency
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.common.ammunition_panel.ammunition_groups_controller import AmmunitionGroupsController, GroupData
from gui.impl.common.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.common.ammunition_panel.ammunition_blocks_controller import BaseAmmunitionBlocksController
from gui.impl.common.ammunition_panel.ammunition_panel_blocks import ConsumablesBlock, ShellsBlock, OptDeviceBlock, BattleBoostersBlock
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_shells_section import AmmunitionShellsSection
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from last_stand.gui.impl.gen.view_models.views.lobby.ext_ammo_panel_view import ExtAmmoPanelView
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants
from last_stand.gui.ls_gui_constants import LS_ABILITY_TOOLTIP, LS_MAIN_SHELL, AmmoPanelSwitchPreset
from last_stand.gui.ls_account_settings import getSettings, AccountSettingsKeys, setSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from skeletons.gui.impl import IGuiLoader
from LSAccountEquipmentController import getLSConsumables
AMMO_SECTIONS_DEFAULT = (TankSetupConstants.SHELLS,
 LSTankSetupConstants.LS_CONSUMABLES,
 TankSetupConstants.OPT_DEVICES,
 TankSetupConstants.BATTLE_BOOSTERS)
AMMO_SECTIONS_ALTERNATIVE = (LSTankSetupConstants.LS_CONSUMABLES,
 TankSetupConstants.SHELLS,
 TankSetupConstants.OPT_DEVICES,
 TankSetupConstants.BATTLE_BOOSTERS)
_PRESET_AMMO_SECTIONS = {AmmoPanelSwitchPreset.PRESET_1: AMMO_SECTIONS_DEFAULT,
 AmmoPanelSwitchPreset.PRESET_2: AMMO_SECTIONS_ALTERNATIVE,
 'default': AMMO_SECTIONS_DEFAULT}
_CMD_KEYS_123 = ('CMD_AMMO_CHOICE_1', 'CMD_AMMO_CHOICE_2', 'CMD_AMMO_CHOICE_3')
_CMD_KEYS_456 = ('CMD_AMMO_CHOICE_4', 'CMD_AMMO_CHOICE_5', 'CMD_AMMO_CHOICE_6')
_PRESET_MAP_AMMO_KEYS = {AmmoPanelSwitchPreset.PRESET_1: (_CMD_KEYS_123, _CMD_KEYS_456),
 AmmoPanelSwitchPreset.PRESET_2: (_CMD_KEYS_456, _CMD_KEYS_123),
 'default': (_CMD_KEYS_123, _CMD_KEYS_456)}
_TOOLTIPS_OVERRIDES = {TOOLTIPS_CONSTANTS.HANGAR_MODULE: LS_ABILITY_TOOLTIP,
 TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL: LS_MAIN_SHELL}

class LSAmmunitionPanelView(HangarAmmunitionPanelView):
    _VIEW_MODEL = ExtAmmoPanelView

    def _addListeners(self):
        super(LSAmmunitionPanelView, self)._addListeners()
        self.viewModel.onSwitch += self.changeGroupsPreset

    def _removeListeners(self):
        super(LSAmmunitionPanelView, self)._removeListeners()
        self.viewModel.onSwitch -= self.changeGroupsPreset

    def changeGroupsPreset(self):
        self._ammunitionPanel.switchToNextPreset()

    def _createAmmunitionPanel(self):
        return LSAmmunitionPanel(self.viewModel.ammunitionPanel, self.vehItem)

    def _getBackportTooltipData(self, event):
        data = super(LSAmmunitionPanelView, self)._getBackportTooltipData(event)
        override = _TOOLTIPS_OVERRIDES.get(data.specialAlias, data.specialAlias)
        return TooltipData(data.tooltip, data.isSpecial, override, data.specialArgs, data.isWulfTooltip)

    def _updateViewModel(self):
        pass


class LSAmmunitionPanel(BaseAmmunitionPanel):

    def switchToNextPreset(self):
        self._controller.setNextPreset()

    def fullUpdateGroups(self):
        with self.viewModel.transaction() as model:
            self._controller.createGroupsModels(model.getSectionGroups())
            model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)

    def _createAmmunitionGroupsController(self, vehicle):
        return LSHangarAmmunitionGroupsController(vehicle, ctx=self._ctx)

    def updateSectionsWithKeySettings(self):
        super(LSAmmunitionPanel, self).updateSectionsWithKeySettings()
        with self.viewModel.transaction() as model:
            self._controller.updateGroupSectionModel(LSTankSetupConstants.LS_CONSUMABLES, model.getSectionGroups())
            model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)


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
    __slots__ = ('_presetCycle',)
    _guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, vehicle, autoCreating=True, ctx=None):
        super(LSHangarAmmunitionGroupsController, self).__init__(vehicle, autoCreating=autoCreating, ctx=ctx)
        self._presetCycle = cycle(AmmoPanelSwitchPreset.ALL)

    def finalize(self):
        super(LSHangarAmmunitionGroupsController, self).finalize()
        self._presetCycle = None
        return

    def setNextPreset(self):
        currentPreset = self._getPreset()
        nextPreset = next((preset for preset in self._presetCycle if preset != currentPreset), AmmoPanelSwitchPreset.PRESET_1)
        self._setPreset(nextPreset)
        ammoPanels = [R.views.last_stand.mono.lobby.ammunition_setup(), R.views.lobby.tanksetup.AmmunitionPanel()]
        views = self._guiLoader.windowsManager.findViews(lambda view: view.layoutID in ammoPanels)
        for view in views:
            view._ammunitionPanel.fullUpdateGroups()

    def _getGroups(self):
        if self._vehicle is None:
            return []
        else:
            ammoSections = _PRESET_AMMO_SECTIONS.get(self._getPreset(), 'default')
            lsGroups = (GroupData(AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS, ammoSections), GroupData(AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS, ()))
            return lsGroups

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return LSAmmunitionBlocksController(vehicle, ctx=ctx)

    @staticmethod
    def _setPreset(presetNum):
        setSettings(AccountSettingsKeys.AMMO_PANEL_PRESET, presetNum)

    @staticmethod
    def _getPreset():
        return getSettings(AccountSettingsKeys.AMMO_PANEL_PRESET)
