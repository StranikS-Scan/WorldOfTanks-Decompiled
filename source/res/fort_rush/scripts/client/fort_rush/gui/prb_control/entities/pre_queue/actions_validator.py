# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/prb_control/entities/pre_queue/actions_validator.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from helpers import dependency

class FortRushBattleVehicleValidator(BaseActionsValidator):
    _battleController = dependency.descriptor(IFortRushBattleController)

    def _validate(self):
        if g_currentVehicle.isPresent():
            restriction = self._battleController.isSuitableVehicle(g_currentVehicle.item)
            if restriction is not None:
                return restriction
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_NO_SUITABLE_VEHICLES, ctx={'levels': [10]}) if not self._battleController.hasSuitableVehicles() else None


class FortRushBattleActionsValidator(PreQueueActionsValidator):

    def __init__(self, entity):
        self._vehicleValidatorExt = FortRushBattleVehicleValidator(entity)
        super(FortRushBattleActionsValidator, self).__init__(entity)

    def _createVehiclesValidator(self, entity):
        baseValidator = super(FortRushBattleActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [self._vehicleValidatorExt, baseValidator])
