# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightPrimeTimeValidator(BaseActionsValidator):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def _validate(self):
        status, _, isInPrimeTime = self.__comp7LightController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE) if not self.__comp7LightController.isAvailable() or not isInPrimeTime else super(Comp7LightPrimeTimeValidator, self)._validate()


class Comp7LightPlayerValidator(BaseActionsValidator):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def _validate(self):
        if self.__comp7LightController.isOffline:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_OFFLINE)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.BAN_IS_SET) if self.__comp7LightController.isBanned else super(Comp7LightPlayerValidator, self)._validate()


class Comp7LightVehicleValidator(BaseActionsValidator):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def _validate(self):
        if g_currentVehicle.isPresent():
            restriction = self.__comp7LightController.isSuitableVehicle(g_currentVehicle.item)
            if restriction is not None:
                return restriction
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_NO_SUITABLE_VEHICLES, ctx={'levels': self.__comp7LightController.getModeSettings().levels}) if not self.__comp7LightController.hasSuitableVehicles() else None


class Comp7LightActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(Comp7LightActionsValidator, self)._createStateValidator(entity)
        validators = [baseValidator, Comp7LightPrimeTimeValidator(entity), Comp7LightPlayerValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)

    def _createVehiclesValidator(self, entity):
        baseValidator = super(Comp7LightActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [Comp7LightVehicleValidator(entity), baseValidator])
