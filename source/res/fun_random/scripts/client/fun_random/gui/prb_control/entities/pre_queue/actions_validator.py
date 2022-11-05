# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.periodic_battles.prb_control.actions_validator import PrimeTimeValidator, BaseActionsValidator

class FunRandomPrimeTimeValidator(PrimeTimeValidator, FunSubModesWatcher):

    def _getController(self):
        return self.getDesiredSubMode()


class FunRandomVehicleValidator(BaseActionsValidator, FunSubModesWatcher):

    def _validate(self):
        validationResult = None
        if g_currentVehicle.isPresent():
            validationResult = self.__validate(g_currentVehicle.item)
        return validationResult or super(FunRandomVehicleValidator, self)._validate()

    @hasDesiredSubMode()
    def __validate(self, vehicle):
        return self.getDesiredSubMode().isSuitableVehicle(vehicle)


class FunRandomActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(FunRandomActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, FunRandomPrimeTimeValidator(entity)])

    def _createVehiclesValidator(self, entity):
        baseValidator = super(FunRandomActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [FunRandomVehicleValidator(entity), baseValidator])
