# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/pre_queue/actions_validator.py
from gui.prb_control.settings import PREBATTLE_RESTRICTION, PRE_QUEUE_RESTRICTION
from helpers import dependency
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController

class LastStandStateValidator(BaseActionsValidator):
    lsCtrl = dependency.descriptor(ILSController)

    def _validate(self):
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE) if not self.lsCtrl.isBattlesEnabled() else super(LastStandStateValidator, self)._validate()


class LastStandVehiclesValidator(BaseActionsValidator):
    lsCtrl = dependency.descriptor(ILSController)
    __difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)

    def _validate(self):
        vehicle = g_currentVehicle.item
        if vehicle:
            vehLimits = self.lsCtrl.getVehiclesConfig()
            if vehicle.intCD not in vehLimits.allowedVehicles:
                if vehicle.level not in vehLimits.allowedLevels or vehicle.intCD in vehLimits.forbiddenVehicles or vehicle.type in vehLimits.forbiddenClassTags:
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
        else:
            return ValidationResult(False)
        return super(LastStandVehiclesValidator, self)._validate()


class LastStandActionsValidator(PreQueueActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(LastStandActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [LastStandVehiclesValidator(entity), LastStandStateValidator(entity), baseValidator])
