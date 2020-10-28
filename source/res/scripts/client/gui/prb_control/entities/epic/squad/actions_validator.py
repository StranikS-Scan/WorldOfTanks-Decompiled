# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, SPGForbiddenSquadVehiclesValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.prb_control.entities.base.unit.actions_validator import UnitStateValidator
from helpers import time_utils, dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class _EpicVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return not vehicle.isEvent


class _EpicStateValidator(UnitStateValidator):
    __epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def _validate(self):
        currentSeason = self.__epicCtrl.getCurrentSeason()
        if currentSeason:
            if currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                return super(_EpicStateValidator, self)._validate()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_UNDEF)


class EpicSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[BalancedSquadVehiclesValidator(entity), _EpicVehiclesValidator(entity), SPGForbiddenSquadVehiclesValidator(entity)])

    def _createStateValidator(self, entity):
        return _EpicStateValidator(entity)
