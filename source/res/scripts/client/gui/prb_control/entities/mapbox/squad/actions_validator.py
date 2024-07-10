# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/mapbox/squad/actions_validator.py
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitStateValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, RoleForbiddenSquadVehiclesValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IMapboxController

class _MapboxStateValidator(UnitStateValidator):

    def _validate(self):
        mapboxCtrl = dependency.instance(IMapboxController)
        status, _, _ = mapboxCtrl.getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.CURFEW) if status != PrimeTimeStatus.AVAILABLE else super(_MapboxStateValidator, self)._validate()


class _UnitSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class MapboxSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[BalancedSquadVehiclesValidator(entity), SquadVehiclesValidator(entity), RoleForbiddenSquadVehiclesValidator(entity)])

    def _createStateValidator(self, entity):
        return _MapboxStateValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(MapboxSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, _UnitSlotsValidator(entity)])
