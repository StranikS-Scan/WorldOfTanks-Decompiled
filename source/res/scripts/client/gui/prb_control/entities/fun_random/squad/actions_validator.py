# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, SPGForbiddenSquadVehiclesValidator, BalancedSquadSlotsValidator
from gui.periodic_battles.prb_control.actions_validator import SquadPrimeTimeValidator
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class _FunRandomSquadStateValidator(SquadPrimeTimeValidator):
    _controller = dependency.descriptor(IFunRandomController)


class _FunRandomSquadVehicleValidator(SquadVehiclesValidator):
    __funRandomController = dependency.descriptor(IFunRandomController)

    def _isVehicleSuitableForMode(self, vehicle):
        validationResult = self.__funRandomController.isSuitableVehicle(vehicle, isSquad=True)
        return validationResult or super(_FunRandomSquadVehicleValidator, self)._isVehicleSuitableForMode(vehicle)


class FunRandomActionsValidator(SquadActionsValidator):

    def _createStateValidator(self, entity):
        return _FunRandomSquadStateValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(FunRandomActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, BalancedSquadSlotsValidator(entity)])

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[_FunRandomSquadVehicleValidator(entity), BalancedSquadVehiclesValidator(entity), SPGForbiddenSquadVehiclesValidator(entity)])
