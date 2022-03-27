# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_bootcamp/pre_queue/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator, BaseActionsValidator
from gui.periodic_battles.prb_control.actions_validator import PrimeTimeValidator
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController

class RTSPrimeTimeValidator(PrimeTimeValidator):
    _controller = dependency.descriptor(IRTSBattlesController)


class RTSBootcampActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(RTSBootcampActionsValidator, self)._createStateValidator(entity)
        validators = [baseValidator, RTSPrimeTimeValidator(entity)]
        return ActionsValidatorComposite(entity, validators)

    def _createVehiclesValidator(self, entity):
        return BaseActionsValidator(entity)
