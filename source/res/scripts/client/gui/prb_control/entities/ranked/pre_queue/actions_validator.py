# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedPrimeTimeValidator(BaseActionsValidator):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _validate(self):
        status, _, _ = self.__rankedController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET, None)
        else:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED, None) if status != PrimeTimeStatus.AVAILABLE else super(RankedPrimeTimeValidator, self)._validate()


class RankedVehicleValidator(BaseActionsValidator):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _validate(self):
        if g_currentVehicle.isPresent():
            restriction = self.__rankedController.isSuitableVehicle(g_currentVehicle.item)
            if restriction is not None:
                return restriction
        return super(RankedVehicleValidator, self)._validate()


class RankedActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(RankedActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, RankedPrimeTimeValidator(entity)])

    def _createVehiclesValidator(self, entity):
        baseValidator = super(RankedActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [RankedVehicleValidator(entity), baseValidator])
