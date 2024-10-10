# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/actions_validator.py
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.entities.base.actions_validator import CurrentVehicleActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION, PRE_QUEUE_RESTRICTION
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger.gui.gui_constants import VEHICLE_TAGS

class WhiteTigerCurrentVehicleActionsValidator(CurrentVehicleActionsValidator):
    __wtController = dependency.descriptor(IWhiteTigerController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def _validate(self):
        vehicle = self.__prebattleVehicle.item
        if not vehicle:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT)
        elif vehicle.isInBattle or vehicle.isDisabled:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE)
        elif not vehicle.isCrewFull:
            return ValidationResult(False, PREBATTLE_RESTRICTION.CREW_NOT_FULL)
        elif vehicle.isBroken:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_BROKEN)
        elif vehicle.rentalIsOver:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_RENTALS_IS_OVER)
        elif vehicle.isUnsuitableToQueue:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        else:
            if VEHICLE_TAGS.WT_BOSS in vehicle.tags and VEHICLE_TAGS.WT_SPECIAL_BOSS not in vehicle.tags:
                if not self.__wtController.hasEnoughTickets():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.TICKETS_SHORTAGE)
            return None


class WhiteTigerBattleActionsValidator(PreQueueActionsValidator):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def _validate(self):
        status, _, _ = self.__wtController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE) if status != PrimeTimeStatus.AVAILABLE else super(WhiteTigerBattleActionsValidator, self)._validate()

    def _createVehiclesValidator(self, entity):
        return WhiteTigerCurrentVehicleActionsValidator(entity)
