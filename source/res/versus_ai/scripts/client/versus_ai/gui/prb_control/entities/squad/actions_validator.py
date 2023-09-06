# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/prb_control/entities/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, SPGForbiddenSquadVehiclesValidator, ScoutForbiddenSquadVehiclesValidator, BalancedSquadSlotsValidator

class _VersusAIVehicleValidator(SquadVehiclesValidator):
    pass


class VersusAISquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[BalancedSquadVehiclesValidator(entity),
         _VersusAIVehicleValidator(entity),
         SPGForbiddenSquadVehiclesValidator(entity),
         ScoutForbiddenSquadVehiclesValidator(entity)])

    def _createSlotsValidator(self, entity):
        baseValidator = super(VersusAISquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, BalancedSquadSlotsValidator(entity)])
