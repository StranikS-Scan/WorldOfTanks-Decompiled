# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/maps_training/pre_queue/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IMapsTrainingController

class MapsTrainingValidator(BaseActionsValidator):
    mapsTrainingController = dependency.descriptor(IMapsTrainingController)

    def _validate(self):
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED) if not self.mapsTrainingController.isValid() else super(MapsTrainingValidator, self)._validate()


class MapsTrainingActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(MapsTrainingActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, MapsTrainingValidator(entity)])

    def _createVehiclesValidator(self, entity):
        return BaseActionsValidator(entity)

    def _createTutorialValidator(self, entity):
        return BaseActionsValidator(entity)
