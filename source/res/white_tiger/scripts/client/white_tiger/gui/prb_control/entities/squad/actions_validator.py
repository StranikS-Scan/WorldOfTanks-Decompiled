# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/actions_validator.py
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator, UnitStateValidator
from gui.prb_control.settings import UNIT_RESTRICTION
from constants import VEHICLE_CLASS_INDICES
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.prb_control.items import ValidationResult, unit_items
from helpers import dependency
from shared_utils import findFirst
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IWhiteTigerController
from gui.periodic_battles.models import PrimeTimeStatus

class _WhiteTigerBattleVehiclesValidator(SquadVehiclesValidator):
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

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
        return ValidationResult(False, UNIT_RESTRICTION.EVENT_VEHICLE_NOT_SELECTED) if not self._isValidMode(vehicle) else None

    def _isValidMode(self, vehicle):
        return VEHICLE_TAGS.EVENT_HUNTER in vehicle.tags


class _WhiteTigerStateValidator(UnitStateValidator):
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    def _validate(self):
        status, _, _ = self.__gameEventCtrl.getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_UNDEF) if status != PrimeTimeStatus.AVAILABLE else super(_WhiteTigerStateValidator, self)._validate()


class WhiteTigerSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        roster = self._entity.getRoster()
        pInfo = self._entity.getPlayerInfo()
        hasEmptySlots = roster.MAX_SLOTS > stats.readyCount + roster.MAX_EMPTY_SLOTS
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if hasEmptySlots or not pInfo.isReady else None


class WhiteTigerBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return _WhiteTigerBattleVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(WhiteTigerBattleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, WhiteTigerSquadSlotsValidator(entity)])

    def _createStateValidator(self, entity):
        return _WhiteTigerStateValidator(entity)
