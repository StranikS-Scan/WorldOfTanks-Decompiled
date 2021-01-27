# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.shared.prime_time_constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IEventProgressionController

class BattleRoyaleValidator(BaseActionsValidator):

    def _validate(self):
        epc = dependency.instance(IEventProgressionController)
        status, _, _ = epc.getPrimeTimeStatus()
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_DISABLED) if g_currentVehicle.isOnlyForBattleRoyaleBattles() and status != PrimeTimeStatus.AVAILABLE else super(BattleRoyaleValidator, self)._validate()


class BattleRoyaleActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(BattleRoyaleActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, BattleRoyaleValidator(entity)])
