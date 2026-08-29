# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/consumables_panel.py
from __future__ import absolute_import
import CommandMapping
import SoundGroups
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel, TOOLTIP_FORMAT
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.items_parameters.shell_params import ShellParams
from gui.shared.tooltips.consumables_panel import TOOLTIP_NO_BODY_FORMAT
from gui.shared.utils.key_mapping import getScaleformKey
from fall_tanks.gui.battle_control.fall_tanks_battle_constants import VEHICLE_VIEW_STATE
from fall_tanks.gui.fall_tanks_gui_constants import FALL_TANKS_SUB_MODE_IMAGES_PATH
from fall_tanks.gui.feature.fall_tanks_sounds import FallTanksSounds

class EvacuationAbilityState(object):
    DEFAULT = 'default'
    READY = 'ready'
    HELD = 'held'


class FallTanksConsumablesPanel(ConsumablesPanel):
    _AMMO_START_IDX = 0
    _AMMO_END_IDX = 0
    _EQUIPMENT_START_IDX = 1
    _EQUIPMENT_END_IDX = 2
    _EVACUATION_SLOT_IDX = 3
    _EVACUATION_HELD_ANIMATION = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_GREEN
    _EVACUATION_CMD_KEY = CommandMapping.CMD_REQUEST_RECOVERY
    _PANEL_MAX_LENGTH = 4
    _ORDERS_START_IDX = 5
    _ORDERS_END_IDX = 4
    _R_ARTEFACT_ICON = FALL_TANKS_SUB_MODE_IMAGES_PATH.ability.small

    def __init__(self):
        super(FallTanksConsumablesPanel, self).__init__()
        self._evacuationIsActive = False
        self._evacuationState = EvacuationAbilityState.DEFAULT
        self._evacuationHoldDuration = None
        textPath = R.strings.fall_tanks.evacuationAbilityTooltip
        self._evacuationTooltip = TOOLTIP_FORMAT.format(backport.text(textPath.name()), backport.text(textPath.description()))
        return

    def _getAmmoIcon(self, icon):
        return backport.image(FALL_TANKS_SUB_MODE_IMAGES_PATH.ammopanel.battle_ammo.fall_tanks_custom_shell())

    def _buildEquipmentSlotTooltipText(self, item):
        tooltipStr = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
        descriptor = item.getDescriptor()
        cooldownTime = backport.getNiceNumberFormat(descriptor.cooldownSeconds)
        body = text_styles.concatStylesToMultiLine(backport.text(R.strings.fall_tanks.ability.name()), backport.text(tooltipStr, cooldownSeconds=cooldownTime), descriptor.description)
        return TOOLTIP_FORMAT.format(descriptor.userString, body)

    def _makeShellTooltip(self, descriptor, gunSettings):
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

    def _addOptionalDeviceSlot(self, idx, optDeviceInBattle):
        pass

    def _resetOptDevices(self):
        pass

    def _updateOptionalDeviceSlot(self, idx, optDeviceInBattle):
        pass

    def _populate(self):
        super(FallTanksConsumablesPanel, self)._populate()
        self._addEvacuationSlot()

    def _reset(self):
        super(FallTanksConsumablesPanel, self)._reset()
        self._addEvacuationSlot()

    def _resetEquipments(self):
        super(FallTanksConsumablesPanel, self)._resetEquipments()
        self._addEvacuationSlot()

    def _onVehicleStateUpdated(self, state, value):
        super(FallTanksConsumablesPanel, self)._onVehicleStateUpdated(state, value)
        if state == VEHICLE_VIEW_STATE.VEHICLE_EVACUATION:
            self._evacuationHoldDuration = value.totalTime
            self._onEvacuationStateChanged(value)

    def _onMappingChanged(self, *args):
        super(FallTanksConsumablesPanel, self)._onMappingChanged(*args)
        bwKey, sfKey = self._getEvacuationKeys()
        if bwKey is not None:
            self.as_setKeysToSlotsS([(self._EVACUATION_SLOT_IDX, bwKey, sfKey)])
        self.as_updateTooltipS(self._EVACUATION_SLOT_IDX, self._evacuationTooltip)
        return

    def _addEvacuationSlot(self):
        bwKey, sfKey = self._getEvacuationKeys()
        self.as_addEquipmentSlotS(idx=self._EVACUATION_SLOT_IDX, keyCode=bwKey if bwKey is not None else 0, sfKeyCode=sfKey, quantity=1, timeRemaining=0, reloadingTime=0, iconPath=backport.image(self._R_ARTEFACT_ICON.fall_tanks_ability_evacuation()), tooltipText=self._evacuationTooltip, animation=ANIMATION_TYPES.NONE)
        self._evacuationState = EvacuationAbilityState.DEFAULT
        return

    def _getEvacuationKeys(self):
        bwKey, _ = CommandMapping.g_instance.getCommandKeys(self._EVACUATION_CMD_KEY)
        return (None, 0) if bwKey is None else (bwKey, getScaleformKey(bwKey))

    def _onEvacuationStateChanged(self, value):
        wasActive = self._evacuationIsActive
        self._evacuationIsActive = value.isActive
        if wasActive and not self._evacuationIsActive and value.endTime == 0.0:
            self._evacuationState = EvacuationAbilityState.READY
            self.as_setItemTimeQuantityInSlotS(self._EVACUATION_SLOT_IDX, 1, 0, 0, ANIMATION_TYPES.GREEN_GLOW_SHOW)
            self._showEquipmentGlow(self._EVACUATION_SLOT_IDX, CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN)
            return
        self._recomputeEvacuationVisual()

    def _hideEquipmentGlowCallback(self, equipmentIndex):
        super(FallTanksConsumablesPanel, self)._hideEquipmentGlowCallback(equipmentIndex)
        if equipmentIndex == self._EVACUATION_SLOT_IDX and self._evacuationState == EvacuationAbilityState.READY:
            self._evacuationState = EvacuationAbilityState.DEFAULT
            self._recomputeEvacuationVisual()

    def _recomputeEvacuationVisual(self):
        target = EvacuationAbilityState.HELD if self._evacuationIsActive else EvacuationAbilityState.DEFAULT
        if target == self._evacuationState:
            return
        if self._evacuationState == EvacuationAbilityState.READY and target == EvacuationAbilityState.DEFAULT:
            return
        self._evacuationState = target
        if target == EvacuationAbilityState.HELD:
            self.as_hideGlowS(self._EVACUATION_SLOT_IDX)
            self.as_setItemTimeQuantityInSlotS(self._EVACUATION_SLOT_IDX, 1, self._evacuationHoldDuration, self._evacuationHoldDuration, self._EVACUATION_HELD_ANIMATION)
        else:
            self.as_setCoolDownTimeS(self._EVACUATION_SLOT_IDX, 0, 0, 0)
            self.as_hideGlowS(self._EVACUATION_SLOT_IDX)
