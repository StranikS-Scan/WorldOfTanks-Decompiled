# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/tournament/unit/actions_validator.py
from gui.prb_control.entities.base.squad.actions_validator import UnitActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitVehiclesValidator, CommanderValidator, UnitStateValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class TournamentVehiclesValidator(UnitVehiclesValidator):
    pass


class TournamentUnitSlotsValidator(CommanderValidator):

    def _validate(self):
        rosterSettings = self._entity.getRosterSettings()
        stats = self._entity.getStats()
        isPlayersMatchingAvailable = self._entity.isPlayersMatchingAvailable()
        allMembersReady = stats.readyCount == stats.occupiedSlotsCount
        if isPlayersMatchingAvailable:
            isClanMembersEnough = stats.clanMembersInRoster >= rosterSettings.getMinClanMembersCount()
            if not isClanMembersEnough:
                return ValidationResult(False, UNIT_RESTRICTION.UNIT_MIN_CLAN_MEMBERS)
            if not allMembersReady:
                return ValidationResult(False, UNIT_RESTRICTION.NOT_READY_IN_SLOTS)
            if stats.occupiedSlotsCount < rosterSettings.getMaxSlots() + 1:
                return ValidationResult(True, UNIT_RESTRICTION.UNIT_WILL_SEARCH_PLAYERS)
        else:
            if rosterSettings.getMinSlots() > stats.occupiedSlotsCount:
                return ValidationResult(False, UNIT_RESTRICTION.MIN_SLOTS)
            if not allMembersReady:
                return ValidationResult(False, UNIT_RESTRICTION.NOT_READY_IN_SLOTS)
        return super(TournamentUnitSlotsValidator, self)._validate()


class TournamentUnitStateValidator(UnitStateValidator):

    def _validate(self):
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_IS_IN_PLAYERS_MATCHING) if self._entity.inPlayersMatchingMode() else super(TournamentUnitStateValidator, self)._validate()


class TournamentActionsValidator(UnitActionsValidator):

    def _createVehiclesValidator(self, entity):
        return TournamentVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        return TournamentUnitSlotsValidator(entity)

    def _createStateValidator(self, entity):
        return TournamentUnitStateValidator(entity)
