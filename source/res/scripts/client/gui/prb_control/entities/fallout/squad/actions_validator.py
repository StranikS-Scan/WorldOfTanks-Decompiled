# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/squad/actions_validator.py
from UnitBase import ROSTER_TYPE
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitVehiclesValidator, CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from shared_utils import findFirst

class FalloutVehiclesValidator(UnitVehiclesValidator):

    def _validate(self):
        """
        Note: We should rid this off when we'll remove fallout, til then - no validation inheritance
        Returns:
        """
        from gui.shared.gui_items.Vehicle import Vehicle
        vInfos = self._entity.getVehiclesInfo()
        if not findFirst(lambda v: not v.isEmpty(), vInfos, False):
            return ValidationResult(False, UNIT_RESTRICTION.FALLOUT_VEHICLE_MIN)
        else:
            for vInfo in vInfos:
                vehicle = vInfo.getVehicle()
                if vehicle is None:
                    continue
                if vehicle.isReadyToPrebattle():
                    if vehicle.isBroken:
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_BROKEN)
                    if not vehicle.isCrewFull:
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_CREW_NOT_FULL)
                    if not self._isValidateRent(vehicle):
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_RENT_IS_OVER)
                    if vehicle.isInBattle:
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_IS_IN_BATTLE)
                    isGroupReady, state = vehicle.isGroupReady()
                    if not isGroupReady:
                        if state == Vehicle.VEHICLE_STATE.FALLOUT_REQUIRED:
                            return ValidationResult(False, UNIT_RESTRICTION.FALLOUT_VEHICLE_LEVEL_REQUIRED)
                        if state == Vehicle.VEHICLE_STATE.FALLOUT_MIN:
                            return ValidationResult(False, UNIT_RESTRICTION.FALLOUT_VEHICLE_MIN)
                        if state == Vehicle.VEHICLE_STATE.FALLOUT_MAX:
                            return ValidationResult(False, UNIT_RESTRICTION.FALLOUT_VEHICLE_MAX)
                        if state == Vehicle.VEHICLE_STATE.FALLOUT_BROKEN:
                            return ValidationResult(False, UNIT_RESTRICTION.FALLOUT_VEHICLE_BROKEN)
                    return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID)

            return


class FalloutSlotsValidator(CommanderValidator):

    def _validate(self):
        roster = self._entity.getRosterSettings()
        stats = self._entity.getStats()
        if stats.freeSlotsCount > roster.getMaxEmptySlots():
            return ValidationResult(False, UNIT_RESTRICTION.FALLOUT_NOT_ENOUGH_PLAYERS)
        return ValidationResult(False, UNIT_RESTRICTION.FALLOUT_NOT_ENOUGH_PLAYERS) if stats.readyCount != stats.occupiedSlotsCount else super(FalloutSlotsValidator, self)._validate()

    def _isEnabled(self):
        return self._entity.getRosterType() == ROSTER_TYPE.FALLOUT_MULTITEAM_ROSTER and super(FalloutSlotsValidator, self)._isEnabled()


class FalloutSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return FalloutVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        return FalloutSlotsValidator(entity)
