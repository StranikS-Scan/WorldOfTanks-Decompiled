# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.gui_items.Vehicle import Vehicle
from shared_utils import findFirst

class UnitStateValidator(BaseActionsValidator):

    def _validate(self):
        flags = self._entity.getFlags()
        if flags.isInArena():
            return ValidationResult(False, UNIT_RESTRICTION.IS_IN_ARENA)
        return ValidationResult(False, UNIT_RESTRICTION.IS_IN_IDLE) if flags.isInIdle() else super(UnitStateValidator, self)._validate()


class UnitPlayerValidator(BaseActionsValidator):

    def _validate(self):
        pInfo = self._entity.getPlayerInfo()
        if not pInfo.isInSlot:
            flags = self._entity.getFlags()
            if flags.isLocked():
                return ValidationResult(False, UNIT_RESTRICTION.UNIT_IS_LOCKED)
            return ValidationResult(False, UNIT_RESTRICTION.NOT_IN_SLOT)
        return super(UnitPlayerValidator, self)._validate()


class UnitVehiclesValidator(BaseActionsValidator):

    def _validate(self):
        vInfos = self._getVehiclesInfo()
        if not findFirst(lambda v: not v.isEmpty(), vInfos, False):
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_SELECTED)
        else:
            for vInfo in vInfos:
                vehicle = vInfo.getVehicle()
                if vehicle is not None:
                    vehicleIsNotSuitableForMode = self._isVehicleSuitableForMode(vehicle)
                    if vehicleIsNotSuitableForMode is not None:
                        return vehicleIsNotSuitableForMode
                    if not vehicle.isReadyToPrebattle(checkForRent=self._isCheckForRent()):
                        if vehicle.isBroken:
                            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_BROKEN)
                        if vehicle.isTooHeavy:
                            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_TOO_HEAVY)
                        if not vehicle.isCrewFull:
                            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_CREW_NOT_FULL)
                        if vehicle.rentalIsOver:
                            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_RENT_IS_OVER)
                        if vehicle.isInBattle:
                            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_IS_IN_BATTLE)
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID)
                    state, _ = vehicle.getState()
                    if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE)

            return super(UnitVehiclesValidator, self)._validate()

    def _isValidMode(self, vehicle):
        return not vehicle.isEvent and not vehicle.isOnlyForEpicBattles and not vehicle.isOnlyForBattleRoyaleBattles

    def _isVehicleSuitableForMode(self, vehicle):
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE) if not self._isValidMode(vehicle) else None

    def _isCheckForRent(self):
        return True

    def _getVehiclesInfo(self):
        return self._entity.getVehiclesInfo()


class ExceptDevModeValidator(BaseActionsValidator):

    def _isEnabled(self):
        return not self._entity.getFlags().isDevMode()


class CommanderValidator(ExceptDevModeValidator):

    def _isEnabled(self):
        return self._entity.isCommander() and super(CommanderValidator, self)._isEnabled()


class UnitSlotsValidator(CommanderValidator):

    def _validate(self):
        roster = self._entity.getRosterSettings()
        stats = self._entity.getStats()
        if roster.getMinSlots() > stats.occupiedSlotsCount:
            return ValidationResult(False, UNIT_RESTRICTION.MIN_SLOTS)
        return ValidationResult(False, UNIT_RESTRICTION.NOT_READY_IN_SLOTS) if stats.readyCount != stats.occupiedSlotsCount else super(UnitSlotsValidator, self)._validate()


class UnitLevelsValidator(ExceptDevModeValidator):

    def _validate(self):
        stats = self._entity.getStats()
        if not stats.curTotalLevel:
            return ValidationResult(False, UNIT_RESTRICTION.ZERO_TOTAL_LEVEL)
        roster = self._entity.getRosterSettings()
        if self._areVehiclesSelected(stats) and stats.curTotalLevel < roster.getMinTotalLevel():
            return ValidationResult(False, UNIT_RESTRICTION.MIN_TOTAL_LEVEL, {'level': roster.getMinTotalLevel()})
        return ValidationResult(False, UNIT_RESTRICTION.MAX_TOTAL_LEVEL, {'level': roster.getMaxTotalLevel()}) if stats.curTotalLevel > roster.getMaxTotalLevel() else super(UnitLevelsValidator, self)._validate()

    def _areVehiclesSelected(self, stats):
        return not stats.freeSlotsCount and len(stats.levelsSeq) == stats.occupiedSlotsCount


class UnitActionsValidator(ActionsValidatorComposite):

    def __init__(self, entity):
        self._stateValidator = self._createStateValidator(entity)
        self._playerValidator = self._createPlayerValidator(entity)
        self._vehiclesValidator = self._createVehiclesValidator(entity)
        self._levelsValidator = self._createLevelsValidator(entity)
        self._slotsValidator = self._createSlotsValidator(entity)
        validators = [self._stateValidator,
         self._playerValidator,
         self._vehiclesValidator,
         self._levelsValidator,
         self._slotsValidator]
        super(UnitActionsValidator, self).__init__(entity, validators)

    def getVehiclesValidator(self):
        return self._vehiclesValidator

    def getPlayerValidator(self):
        return self._playerValidator

    def getStateValidator(self):
        return self._stateValidator

    def getLevelsValidator(self):
        return self._levelsValidator

    def getSlotsValidator(self):
        return self._slotsValidator

    def validateStateToStartBattle(self):
        return ValidationResult()

    def _createVehiclesValidator(self, entity):
        return UnitVehiclesValidator(entity)

    def _createPlayerValidator(self, entity):
        return UnitPlayerValidator(entity)

    def _createStateValidator(self, entity):
        return UnitStateValidator(entity)

    def _createLevelsValidator(self, entity):
        return UnitLevelsValidator(entity)

    def _createSlotsValidator(self, entity):
        return UnitSlotsValidator(entity)
