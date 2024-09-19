# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator, UnitStateValidator
from gui.prb_control.settings import UNIT_RESTRICTION
from constants import VEHICLE_CLASS_INDICES
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT
from gui.prb_control.items import ValidationResult, unit_items
from shared_utils import findFirst
from skeletons.gui.game_control import IEventBattlesController
from gui.periodic_battles.models import PrimeTimeStatus
from skeletons.prebattle_vehicle import IPrebattleVehicle
from helpers import dependency

class _EventBattleVehiclesValidator(SquadVehiclesValidator):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def _validate(self):
        leaderEventEnqueueData = self._entity.getLeaderEventEnqueueData()
        if leaderEventEnqueueData is not None:
            result = True
            if not result:
                return ValidationResult(False, UNIT_RESTRICTION.UNIT_WRONG_DATA)
        return super(_EventBattleVehiclesValidator, self)._validate()

    def _getVehiclesInfo(self):
        vInfos = self._entity.getVehiclesInfo()
        if not findFirst(lambda v: not v.isEmpty(), vInfos, False):
            vehicle = self.__prebattleVehicle.item
            if vehicle is not None:
                vehClassIdx = VEHICLE_CLASS_INDICES[vehicle.type]
                vInfos = (unit_items.VehicleInfo(vehicle.invID, vehicle.intCD, vehicle.level, vehClassIdx),)
        return vInfos

    def _getVehicleIsNotSelectedResult(self):
        return ValidationResult(False, UNIT_RESTRICTION.EVENT_VEHICLE_NOT_SELECTED)

    def _isVehicleSuitableForMode(self, vehicle):
        if not self._isValidMode(vehicle):
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE)
        else:
            return ValidationResult(False, UNIT_RESTRICTION.EVENT_VEHICLE_NOT_SELECTED) if vehicle.isBoss else None

    def _isValidMode(self, vehicle):
        return vehicle.isEvent and not bool(vehicle.tags & BATTLE_MODE_VEH_TAGS_EXCEPT_EVENT)


class _EventStateValidator(UnitStateValidator):
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

    def _validate(self):
        status, _, _ = self.__gameEventCtrl.getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_UNDEF) if status != PrimeTimeStatus.AVAILABLE else super(_EventStateValidator, self)._validate()


class EventSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        roster = self._entity.getRoster()
        pInfo = self._entity.getPlayerInfo()
        hasEmptySlots = roster.MAX_SLOTS > stats.readyCount + roster.MAX_EMPTY_SLOTS
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if hasEmptySlots or not pInfo.isReady else None


class EventBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(EventBattleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, EventSquadSlotsValidator(entity)])

    def _createStateValidator(self, entity):
        return _EventStateValidator(entity)
