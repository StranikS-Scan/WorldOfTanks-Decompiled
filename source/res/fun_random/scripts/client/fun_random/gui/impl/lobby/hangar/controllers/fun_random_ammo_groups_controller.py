# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/controllers/fun_random_ammo_groups_controller.py
from __future__ import absolute_import
import typing
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from fun_random.gui.impl.gen.view_models.views.lobby.loadout.fun_random_loadout_constants import FunRandomLoadoutConstants
from fun_random.gui.impl.lobby.hangar.controllers.fun_random_ammo_blocks_controller import FunRandomHangarAmmunitionBlocksController
from gui.impl.common.ammunition_panel.ammunition_groups_controller import GroupData, SWITCHABLE_SECTIONS
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.groups_controller import HangarAmmunitionGroupsController
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.configs.sub_modes.sub_mode import FunSubModeCompositeConfigurationModel

class FunRandomHangarAmmunitionGroupsController(HangarAmmunitionGroupsController, FunSubModesWatcher):
    __slots__ = ()

    def _isSwitchEnabled(self, groupSettings):
        hasSwitchable = bool(set(groupSettings.sections) & set(SWITCHABLE_SECTIONS))
        return hasSwitchable and super(FunRandomHangarAmmunitionGroupsController, self)._isSwitchEnabled(groupSettings)

    def _getGroups(self):
        return self.__getSubModeGroups() if self._vehicle is not None else []

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return FunRandomHangarAmmunitionBlocksController(vehicle, ctx=ctx)

    @hasDesiredSubMode(defReturn=[])
    def __getSubModeGroups(self):
        groups = []
        config = self.getDesiredSubMode().getConfigurationModel()
        sections = []
        if config.common.regularDevices:
            sections.append(TankSetupConstants.OPT_DEVICES)
        if config.common.regularBoosters:
            sections.append(TankSetupConstants.BATTLE_BOOSTERS)
        if sections:
            groups.append(GroupData(AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS, sections))
        sections = []
        if config.common.regularShells:
            sections.append(TankSetupConstants.SHELLS)
        if config.subMode.customShells.exists:
            sections.append(FunRandomLoadoutConstants.FUN_RANDOM_CUSTOM_SHELLS)
        if config.common.regularConsumables:
            sections.append(TankSetupConstants.CONSUMABLES)
        if sections:
            groups.append(GroupData(AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS, sections))
        sections = []
        if config.subMode.customAbilities.exists:
            sections.append(FunRandomLoadoutConstants.FUN_RANDOM_CUSTOM_ABILITIES)
        if sections:
            groups.append(GroupData(FunRandomLoadoutConstants.BATTLE_ABILITIES_GROUP, sections))
        return groups
