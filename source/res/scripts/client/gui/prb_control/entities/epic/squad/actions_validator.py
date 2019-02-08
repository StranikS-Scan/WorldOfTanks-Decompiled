# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, SPGForbiddenSquadVehiclesValidator

class _EpicVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return not vehicle.isEvent


class EpicSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[BalancedSquadVehiclesValidator(entity), _EpicVehiclesValidator(entity), SPGForbiddenSquadVehiclesValidator(entity)])
