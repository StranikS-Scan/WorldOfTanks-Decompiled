# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/prb_control/entities/pre_queue/actions_validator.py
from typing import TYPE_CHECKING
from skeletons.gui.game_control import IRacesBattleController
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from helpers import dependency
from CurrentVehicle import g_currentVehicle
if TYPE_CHECKING:
    from gui.prb_control.entities.base.entity import BasePrbEntity

class RacesBattleVehicleValidator(BaseActionsValidator):
    __racesController = dependency.descriptor(IRacesBattleController)

    def _validate(self):
        vehicleId = g_currentVehicle.item.intCD
        if vehicleId not in self.__racesController.getRacesVehiclesInfo().keys():
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE) if g_currentVehicle.isInBattle() else ValidationResult(True, '')


class RacesValidator(BaseActionsValidator):
    __racesController = dependency.descriptor(IRacesBattleController)

    def _validate(self):
        return ValidationResult(False, PREBATTLE_RESTRICTION.UNDEFINED) if not self.__racesController.isEnabled or self.__racesController.isFrozen() or not self.__racesController.isBattleAvailable() else super(RacesValidator, self)._validate()


class RacesBattleActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(RacesBattleActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, RacesValidator(entity)])

    def _createVehiclesValidator(self, entity):
        return RacesBattleVehicleValidator(entity)
