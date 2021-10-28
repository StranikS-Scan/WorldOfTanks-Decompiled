# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from helpers import dependency
from CurrentVehicle import g_currentPreviewVehicle
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.event.pre_queue.actions_validator import AFKBanValidator as AFKBanValidatorBase
from skeletons.gui.game_event_controller import IGameEventController

class _EventBattleVehiclesValidator(SquadVehiclesValidator):
    gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID) if g_currentPreviewVehicle.isPresent() else super(_EventBattleVehiclesValidator, self)._validate()

    def _isValidMode(self, vehicle):
        return self.gameEventController.isEnabled() and vehicle.isEvent


class AFKBanValidator(AFKBanValidatorBase):
    RESTRICTION = UNIT_RESTRICTION.EVENT_AFK_BAN


class EventSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        roster = self._entity.getRoster()
        pInfo = self._entity.getPlayerInfo()
        hasEmptySlots = roster.MAX_SLOTS > stats.readyCount + roster.MAX_EMPTY_SLOTS
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if hasEmptySlots or not pInfo.isReady else None


class EventBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, [AFKBanValidator(entity), _EventBattleVehiclesValidator(entity)])

    def _createSlotsValidator(self, entity):
        baseValidator = super(EventBattleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, EventSquadSlotsValidator(entity)])
