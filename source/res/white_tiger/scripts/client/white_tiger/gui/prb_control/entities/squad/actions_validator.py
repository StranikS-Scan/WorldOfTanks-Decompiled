# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT
from gui.periodic_battles.prb_control.actions_validator import SquadPrimeTimeValidator
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator
from gui.prb_control.entities.base.squad.components import getRestrictedVehicleClassTag
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController

class WhiteTigerSquadStateValidator(SquadPrimeTimeValidator):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def _getController(self):
        return self.__wtCtrl


class WhiteTigerSquadVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return vehicle.isEvent and not bool(vehicle.tags & BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT)

    def _isVehicleSuitableForMode(self, vehicle):
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID, None) if 'wt_boss' in vehicle.tags else super(WhiteTigerSquadVehiclesValidator, self)._isVehicleSuitableForMode(vehicle)


class WhiteTigerSquadActionsValidator(SquadActionsValidator):

    def _createStateValidator(self, entity):
        return WhiteTigerSquadStateValidator(entity)

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, [WhiteTigerSquadVehiclesValidator(entity)])

    def _createSlotsValidator(self, entity):
        baseValidator = super(WhiteTigerSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, WhiteTigerBalancedSquadSlotsValidator(entity), WhiteTigerRoleValidator(entity)])


class WhiteTigerRoleValidator(BaseActionsValidator):
    ROLE_RESTRICTIONS = {'wt_hunter': UNIT_RESTRICTION.UNIT_IS_FULL,
     'wt_boss': UNIT_RESTRICTION.LIMIT_VEHICLE_CLASS}

    def _validate(self):
        pInfo = self._entity.getPlayerInfo()
        result = super(WhiteTigerRoleValidator, self)._validate()
        if pInfo.isReady or not g_currentVehicle.isPresent():
            return result
        else:
            vehicleTag = getRestrictedVehicleClassTag(g_currentVehicle.item.tags)
            if vehicleTag not in self._entity.squadRestrictions:
                return result
            if not self._entity.hasSlotForRole(vehicleTag):
                result = ValidationResult(False, UNIT_RESTRICTION.UNIT_IS_FULL, None)
            return result


class WhiteTigerBalancedSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED, None) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None
