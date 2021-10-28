# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from skeletons.gui.afk_controller import IAFKController
from helpers import dependency
from gui.prb_control.items import ValidationResult

class AFKBanValidator(BaseActionsValidator):
    afkController = dependency.descriptor(IAFKController)
    RESTRICTION = PREBATTLE_RESTRICTION.EVENT_AFK_BAN

    def _validate(self):
        return ValidationResult(False, self.RESTRICTION) if self.afkController.isBanned else super(AFKBanValidator, self)._validate()


class EventVehicleValidator(BaseActionsValidator):

    def _validate(self):
        return ValidationResult(False, PREBATTLE_RESTRICTION.PREVIEW_VEHICLE_IS_PRESENT) if not g_currentVehicle.isEvent() else super(EventVehicleValidator, self)._validate()


class EventActionsValidator(PreQueueActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(EventActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, AFKBanValidator(entity), EventVehicleValidator(entity)])

    def _validate(self):
        result = super(EventActionsValidator, self)._validate()
        return result
