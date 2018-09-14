# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from gui.shared.gui_items.Vehicle import Vehicle

class FalloutActionsValidator(BaseActionsValidator):

    def _validate(self):
        storage = self._entity.storage
        if not storage.isEnabled():
            return ValidationResult(False)
        if storage.getBattleType() not in QUEUE_TYPE.FALLOUT:
            return ValidationResult(False, PREBATTLE_RESTRICTION.FALLOUT_NOT_SELECTED)
        if not g_currentVehicle.item.isPresent():
            return ValidationResult(False)
        groupReady, state = g_currentVehicle.item.isGroupReady()
        if not groupReady:
            if state == Vehicle.VEHICLE_STATE.FALLOUT_REQUIRED:
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_GROUP_REQUIRED)
            if state == Vehicle.VEHICLE_STATE.FALLOUT_MIN:
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_GROUP_MIN)
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_GROUP_IS_NOT_READY)
        return super(FalloutActionsValidator, self)._validate()
