# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/actions_validator.py
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.squad.actions_validator import UnitActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitVehiclesValidator, CommanderValidator, UnitStateValidator, UnitPlayerValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class StrongholdVehiclesValidator(UnitVehiclesValidator):
    pass


class StrongholdUnitSlotsValidator(CommanderValidator):

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
        return super(StrongholdUnitSlotsValidator, self)._validate()


class StrongholdUnitStateValidator(UnitStateValidator):

    def _validate(self):
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_IS_IN_PLAYERS_MATCHING) if self._entity.inPlayersMatchingMode() else super(StrongholdUnitStateValidator, self)._validate()


class StrongholdUnitPlayerValidator(UnitPlayerValidator):

    def _validate(self):
        if self._entity.inPlayersMatchingMode():
            return ValidationResult(False, UNIT_RESTRICTION.UNIT_IS_IN_PLAYERS_MATCHING)
        return ValidationResult(False, UNIT_RESTRICTION.PLAY_LIMITS_IS_ACTIVE) if prb_getters.isParentControlActivated() else super(StrongholdUnitPlayerValidator, self)._validate()


class StrongholdActionsValidator(UnitActionsValidator):

    def _createVehiclesValidator(self, entity):
        return StrongholdVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        return StrongholdUnitSlotsValidator(entity)

    def _createStateValidator(self, entity):
        return StrongholdUnitStateValidator(entity)

    def _createPlayerValidator(self, entity):
        return StrongholdUnitPlayerValidator(entity)
