# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prb_control/entities/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT
from gui.periodic_battles.prb_control.actions_validator import SquadPrimeTimeValidator
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator
from gui.prb_control.entities.base.squad.components import getRestrictedVehicleClassTag
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from grinch.gui.prb_control.settings import GRINCH_UNIT_RESTRICTION
from grinch.skeletons.battle_controller import IGrinchController
from helpers import dependency

class GrinchSquadStateValidator(SquadPrimeTimeValidator):
    __grinchCtrl = dependency.descriptor(IGrinchController)

    def _getController(self):
        return self.__grinchCtrl


class GrinchSquadVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return vehicle.isEvent and not bool(vehicle.tags & BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT)


class GrinchSquadActionsValidator(SquadActionsValidator):

    def _createStateValidator(self, entity):
        return GrinchSquadStateValidator(entity)

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, [GrinchSquadVehiclesValidator(entity)])

    def _createSlotsValidator(self, entity):
        baseValidator = super(GrinchSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, BalancedSquadSlotsValidator(entity), GrinchRoleValidator(entity)])


class GrinchRoleValidator(BaseActionsValidator):
    ROLE_RESTRICTIONS = {'scout': UNIT_RESTRICTION.SCOUT_IS_FULL,
     'mediumTank': UNIT_RESTRICTION.MEDIUMTANK_IS_FULL,
     'heavyTank': UNIT_RESTRICTION.HEAVYTANK_IS_FULL}

    def _validate(self):
        pInfo = self._entity.getPlayerInfo()
        result = super(GrinchRoleValidator, self)._validate()
        if pInfo.isReady or not g_currentVehicle.isPresent():
            return result
        vehicleTag = getRestrictedVehicleClassTag(g_currentVehicle.item.tags)
        if vehicleTag not in self._entity.squadRestrictions:
            return result
        if not self._entity.hasSlotForRole(vehicleTag):
            result = ValidationResult(False, GRINCH_UNIT_RESTRICTION.ROLE_FULL)
        return result


class BalancedSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None
