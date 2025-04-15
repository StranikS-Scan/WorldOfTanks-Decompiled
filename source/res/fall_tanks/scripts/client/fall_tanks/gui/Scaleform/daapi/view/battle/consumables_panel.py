# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/consumables_panel.py
import SoundGroups
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, TOOLTIP_FORMAT
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.items_parameters.params import ShellParams
from gui.shared.tooltips.consumables_panel import TOOLTIP_NO_BODY_FORMAT
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_IMAGES_PATH
from fall_tanks.gui.feature.fall_tanks_sounds import FallTanksSounds

class FallTanksConsumablesPanel(ConsumablesPanel):
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 0
    _EQUIPMENT_START_IDX = 1
    _EQUIPMENT_END_IDX = 2
    _PANEL_MAX_LENGTH = 3
    _ORDERS_START_IDX = 5
    _ORDERS_END_IDX = 4
    _R_ARTEFACT_ICON = FALL_TANKS_IMAGES_PATH.consumables

    def _getAmmoIcon(self, icon):
        return backport.image(FALL_TANKS_IMAGES_PATH.shells.shell_hud())

    def _buildEquipmentSlotTooltipText(self, item):
        tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
        descriptor = item.getDescriptor()
        cooldownTime = backport.getNiceNumberFormat(descriptor.cooldownSeconds)
        body = text_styles.concatStylesToMultiLine(backport.text(R.strings.fall_tanks.ability.name()), backport.text(tooltipStr, cooldownSeconds=cooldownTime), descriptor.description)
        return TOOLTIP_FORMAT.format(descriptor.userString, body)

    def _makeShellTooltip(self, descriptor, piercingPower, shotSpeed):
        textPath = R.strings.fall_tanks
        header = backport.text(textPath.shellTooltip.header())
        if GUI_SETTINGS.technicalInfo:
            footNote = backport.text(textPath.shellTooltip.description())
            caliber = backport.text(textPath.shellTooltip.caliber(), caliber=backport.getNiceNumberFormat(ShellParams(descriptor).caliber))
            body = text_styles.concatStylesToMultiLine(caliber, footNote)
            fmt = TOOLTIP_FORMAT
        else:
            body = ''
            fmt = TOOLTIP_NO_BODY_FORMAT
        return fmt.format(header, body)

    def _handleEquipmentPressedResult(self, result, error):
        super(FallTanksConsumablesPanel, self)._handleEquipmentPressedResult(result, error)
        SoundGroups.g_instance.playSound2D(FallTanksSounds.ABILITY_TRIGGER)
        if not result and error:
            SoundGroups.g_instance.playSound2D(FallTanksSounds.ABILITY_NOT_READY)

    def _onEquipmentAdded(self, intCD, item):
        if item is not None:
            super(FallTanksConsumablesPanel, self)._onEquipmentAdded(intCD, item)
        return

    def _onNextShellChanged(self, intCD):
        pass

    def _onOptionalDeviceAdded(self, _):
        pass

    def _onOptionalDeviceUpdated(self, optDeviceInBattle):
        pass

    def _addOptionalDeviceSlot(self, idx, intCD):
        pass

    def _resetOptDevices(self):
        pass

    def _updateOptionalDeviceSlot(self, idx, isOn):
        pass
