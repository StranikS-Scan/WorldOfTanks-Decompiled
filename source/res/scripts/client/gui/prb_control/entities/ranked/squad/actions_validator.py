# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/squad/actions_validator.py
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_RANKED
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitSlotsValidator, CommanderValidator, UnitPlayerValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController, IRankedBattlesController
from gui.periodic_battles.models import PrimeTimeStatus
from constants import IS_DEVELOPMENT

class _RankedVehiclesValidator(SquadVehiclesValidator):
    _BATTLE_MODE_VEHICLE_TAGS = BATTLE_MODE_VEH_TAGS_EXCEPT_RANKED


class _UnitSlotsValidator(UnitSlotsValidator):

    def _validate(self):
        stats = self._entity.getStats()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_NOT_FULL) if stats.freeSlotsCount > 0 else super(_UnitSlotsValidator, self)._validate()


class _PrimeTimeValidator(CommanderValidator):

    def _validate(self):
        status, _, _ = dependency.instance(IRankedBattlesController).getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.CURFEW) if status != PrimeTimeStatus.AVAILABLE else super(_PrimeTimeValidator, self)._validate()


class _RankedPlayerValidator(UnitPlayerValidator):
    __rankedCtrl = dependency.descriptor(IRankedBattlesController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def _validate(self):
        ranks, divisions = self.__getPlayersData()
        ranksDiffRestriction = self.__rankedCtrl.getRankSquadRestriction()
        divisionRestriction = self.__rankedCtrl.getDivisionSquadRestriction()
        if ranks and ranksDiffRestriction is not None and max(ranks) - min(ranks) > ranksDiffRestriction:
            return ValidationResult(False, UNIT_RESTRICTION.RANK_RESTRICTION, None)
        else:
            return ValidationResult(False, UNIT_RESTRICTION.DIVISION_RESTRICTION, None) if divisions and divisionRestriction and len(divisions) > 1 else super(_RankedPlayerValidator, self)._validate()

    def __getPlayersData(self):
        playersRank = []
        playersDivision = set()
        for slotData in self.__platoonCtrl.getPlatoonSlotsData():
            playerData = slotData.get('player')
            if playerData is None:
                continue
            rankedEnqueueData = playerData.get('extraData', {}).get('rankedEnqueueData', {})
            playersRank.append(rankedEnqueueData.get('rank', 0))
            playersDivision.add(rankedEnqueueData.get('division', 0))

        return (playersRank, playersDivision)


class _RankedSlotValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class RankedSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        validators = [_RankedVehiclesValidator(entity), _PrimeTimeValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)

    def _createSlotsValidator(self, entity):
        baseValidator = super(RankedSquadActionsValidator, self)._createSlotsValidator(entity)
        validators = [baseValidator, _RankedSlotValidator(entity)]
        if not IS_DEVELOPMENT:
            validators.append(_UnitSlotsValidator(entity))
        return ActionsValidatorComposite(entity, validators=validators)

    def _createPlayerValidator(self, entity):
        validators = [_RankedPlayerValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)
