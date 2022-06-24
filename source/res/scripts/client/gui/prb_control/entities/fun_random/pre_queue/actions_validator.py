# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.periodic_battles.prb_control.actions_validator import PrimeTimeValidator, BaseActionsValidator
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomPrimeTimeValidator(PrimeTimeValidator):
    _controller = dependency.descriptor(IFunRandomController)


class FunRandomVehicleValidator(BaseActionsValidator):
    __funRandomController = dependency.descriptor(IFunRandomController)

    def _validate(self):
        validationResult = None
        if g_currentVehicle.isPresent():
            validationResult = self.__funRandomController.isSuitableVehicle(g_currentVehicle.item)
        return validationResult or super(FunRandomVehicleValidator, self)._validate()


class FunRandomActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(FunRandomActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, FunRandomPrimeTimeValidator(entity)])

    def _createVehiclesValidator(self, entity):
        baseValidator = super(FunRandomActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [FunRandomVehicleValidator(entity), baseValidator])
