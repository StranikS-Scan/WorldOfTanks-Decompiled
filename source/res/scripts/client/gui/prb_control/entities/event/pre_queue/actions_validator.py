# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/actions_validator.py
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.entities.base.actions_validator import CurrentVehicleActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION, PRE_QUEUE_RESTRICTION
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS as _TAGS
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IEventBattlesController

class EventCurrentVehicleActionsValidator(CurrentVehicleActionsValidator):
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def _validate(self):
        vehicle = self.__prebattleVehicle.item
        if not vehicle:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT)
        elif vehicle.isInBattle or vehicle.isDisabled:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE)
        elif vehicle.isTooHeavy:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_TOO_HEAVY)
        elif not vehicle.isCrewFull:
            return ValidationResult(False, PREBATTLE_RESTRICTION.CREW_NOT_FULL)
        elif vehicle.isBroken:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_BROKEN)
        elif vehicle.rentalIsOver:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_RENTALS_IS_OVER)
        elif vehicle.isUnsuitableToQueue:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        else:
            if _TAGS.EVENT_BOSS in vehicle.tags and _TAGS.EVENT_SPECIAL_BOSS not in vehicle.tags:
                if not self.__gameEventCtrl.hasEnoughTickets():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.TICKETS_SHORTAGE)
            return None


class EventBattleActionsValidator(PreQueueActionsValidator):
    __gameEventController = dependency.descriptor(IEventBattlesController)

    def _validate(self):
        status, _, _ = self.__gameEventController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE) if status != PrimeTimeStatus.AVAILABLE else super(EventBattleActionsValidator, self)._validate()

    def _createVehiclesValidator(self, entity):
        return EventCurrentVehicleActionsValidator(entity)
