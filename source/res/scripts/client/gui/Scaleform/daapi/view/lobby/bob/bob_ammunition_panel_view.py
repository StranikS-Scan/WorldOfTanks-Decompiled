# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/bob/bob_ammunition_panel_view.py
import logging
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.bob.bob_vehicle import g_bobVehicle
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.tank_setup.backports.tooltips import OptDeviceTooltipBuilder, ConsumableToolitpBuilder, BattleBoostersTooltipBuilder, ShellTooltipBuilder, BattleAbilitiesToolitpBuilder, getSlotTooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class BobShellTooltipBuilder(ShellTooltipBuilder):

    @classmethod
    def _getInSlotTooltipAlias(cls):
        return TOOLTIPS_CONSTANTS.BOB_TECH_MAIN_SHELL

    @classmethod
    def _getTooltipSpecialAlias(cls):
        return TOOLTIPS_CONSTANTS.BOB_TECH_MAIN_SHELL


PANEL_SLOT_TOOLTIPS = {TankSetupConstants.BATTLE_BOOSTERS: BattleBoostersTooltipBuilder,
 TankSetupConstants.BATTLE_ABILITIES: BattleAbilitiesToolitpBuilder,
 TankSetupConstants.OPT_DEVICES: OptDeviceTooltipBuilder,
 TankSetupConstants.CONSUMABLES: ConsumableToolitpBuilder,
 TankSetupConstants.SHELLS: BobShellTooltipBuilder}

class BobAmmunitionPanelView(HangarAmmunitionPanelView):

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            if self._hangarSpace.spaceLoading():
                _logger.warning('Failed to get slotData. HangarSpace is currently loading.')
                return
            tooltipId = event.getArgument('tooltip')
            if tooltipId != TOOLTIPS_CONSTANTS.HANGAR_SLOT_SPEC:
                tooltipData = getSlotTooltipData(event, self.vehItem, self.viewModel.ammunitionPanel.getSelectedSlot(), tooltipsMap=PANEL_SLOT_TOOLTIPS)
                if tooltipData is not None:
                    window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                    window.load()
                    return window
        return super(BobAmmunitionPanelView, self).createToolTip(event)

    @property
    def vehItem(self):
        return g_bobVehicle.item if g_bobVehicle.isPresent() else g_currentVehicle.item
