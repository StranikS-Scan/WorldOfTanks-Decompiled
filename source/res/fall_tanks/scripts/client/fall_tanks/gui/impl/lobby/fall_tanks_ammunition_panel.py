# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/impl/lobby/fall_tanks_ammunition_panel.py
from gui.impl.backport import createTooltipData
from gui.impl.common.ammunition_panel.ammunition_panel_blocks import ShellsBlock, ConsumablesBlock
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.blocks_controller import HangarAmmunitionBlocksController
from gui.impl.lobby.tank_setup.ammunition_panel.groups_controller import HangarAmmunitionGroupsController
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from items import vehicles
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_IMAGES_PATH, FallTanksTankSetupConstants, FALL_TANKS_EQUIPMENTS, FALL_TANKS_TOOLTIPS_SET

def _getFallTanksHangarAmmoTooltipData(event):
    return createTooltipData(isSpecial=True, specialAlias=event.getArgument('slotType'), specialArgs=[event.getArgument('intCD')])


class FallTanksAmmunitionPanelView(HangarAmmunitionPanelView):

    def _createAmmunitionPanel(self):
        return FallTanksAmmunitionPanel(self.viewModel.ammunitionPanel, self.vehItem)

    def _getBackportTooltipData(self, event):
        return _getFallTanksHangarAmmoTooltipData(event) if event.getArgument('slotType') in FALL_TANKS_TOOLTIPS_SET else super(FallTanksAmmunitionPanelView, self)._getBackportTooltipData(event)

    def _onPanelSectionSelected(self, args):
        if args['selectedSection'] not in (TankSetupConstants.SHELLS, TankSetupConstants.CONSUMABLES):
            super(FallTanksAmmunitionPanelView, self)._onPanelSectionSelected(args)


class FallTanksAmmunitionPanel(HangarAmmunitionPanel):

    def _createAmmunitionGroupsController(self, vehicle):
        return FallTanksHangarAmmunitionGroupsController(vehicle, ctx=self._ctx)


class FallTanksHangarAmmunitionGroupsController(HangarAmmunitionGroupsController):
    __slots__ = ()

    def _createAmmunitionBlockController(self, vehicle, ctx=None):
        return FallTanksAmmunitionBlocksController(vehicle, ctx=ctx)

    def _isSwitchEnabled(self, groupSettings):
        return False if groupSettings.groupID == AmmunitionPanelConstants.EQUIPMENT_AND_SHELLS else super(FallTanksHangarAmmunitionGroupsController, self)._isSwitchEnabled(groupSettings)


class FallTanksAmmunitionBlocksController(HangarAmmunitionBlocksController):
    __slots__ = ()

    @tabUpdateFunc(TankSetupConstants.SHELLS)
    def _updateShells(self, viewModel, isFirst=False):
        FallTanksShellsBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)

    @tabUpdateFunc(TankSetupConstants.CONSUMABLES)
    def _updateConsumables(self, viewModel, isFirst=False):
        FallTanksConsumablesBlock(self._vehicle, self._currentSection).adapt(viewModel, isFirst)


class FallTanksShellsBlock(ShellsBlock):

    def _getSectionName(self):
        return FallTanksTankSetupConstants.FALL_TANK_SHELLS

    def _getInstalled(self):
        return [super(FallTanksShellsBlock, self)._getInstalled()[0]]

    def _getLayout(self):
        return self._getInstalled()

    def _getKeySettings(self):
        pass

    def _updateSlotWithItem(self, model, idx, slotItem):
        model.setIntCD(slotItem.intCD)
        model.setImageSource(FALL_TANKS_IMAGES_PATH.shells.shell_hangar())
        model.setNonRemovable(True)
        model.setOverlayType(FallTanksTankSetupConstants.FALL_TANK_INFINITE_SHELL_OVERLAY)


class FallTanksConsumablesBlock(ConsumablesBlock):

    def _getSectionName(self):
        return FallTanksTankSetupConstants.FALL_TANK_CONSUMABLES

    def _getKeySettings(self):
        pass

    def _getLayout(self):
        return self._getInstalled()

    def _getInstalled(self):
        equipIds = vehicles.g_cache.equipmentIDs()
        allEquip = vehicles.g_cache.equipments()
        return [ allEquip.get(equipIds.get(equipmentName)) for equipmentName in FALL_TANKS_EQUIPMENTS ]

    def _updateSlotWithItem(self, model, idx, equipment):
        model.setImageSource(FALL_TANKS_IMAGES_PATH.consumables.dyn(equipment.iconName)())
        model.setIsInstalled(True)
        model.setItemInstalledSetupIdx(idx)
        model.setIsMountedMoreThanOne(False)
        model.setIntCD(equipment.compactDescr)
        model.setOverlayType(ItemHighlightTypes.EMPTY)
        model.setNonRemovable(True)
