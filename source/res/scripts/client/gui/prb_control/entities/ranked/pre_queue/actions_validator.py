# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.periodic_battles.prb_control.actions_validator import PrimeTimeValidator
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedPrimeTimeValidator(PrimeTimeValidator):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def _getController(self):
        return self.__rankedController


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
