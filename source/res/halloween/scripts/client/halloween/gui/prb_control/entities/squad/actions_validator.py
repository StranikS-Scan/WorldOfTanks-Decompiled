# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.entities.random.squad.actions_validator import RandomSquadActionsValidator, SPGForbiddenSquadVehiclesValidator, BalancedSquadActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from halloween_common.halloween_constants import QUEUE_TYPE

class _HalloweenBattleVehiclesValidator(SquadVehiclesValidator):

    def _validate(self):
        levelsRange = self._entity.getRosterSettings().getLevelsRange()
        pInfo = self._entity.getPlayerInfo()
        if not pInfo.isReady and g_currentVehicle.isPresent() and g_currentVehicle.item.level not in levelsRange:
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL)
        vInfos = self._getVehiclesInfo()
        commanderQueueType = self._entity.getCommanderQueueType()
        if commanderQueueType:
            for vInfo in vInfos:
                vehicle = vInfo.getVehicle()
                isWheeledScout = vehicle.isWheeledTech and vehicle.isScout
                if commanderQueueType == QUEUE_TYPE.HALLOWEEN_BATTLES and isWheeledScout or commanderQueueType == QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL and not isWheeledScout:
                    return ValidationResult(False, UNIT_RESTRICTION.UNSUITABLE_VEHICLE)

        return super(_HalloweenBattleVehiclesValidator, self)._validate()

    def _isValidMode(self, vehicle):
        return super(_HalloweenBattleVehiclesValidator, self)._isValidMode(vehicle) or vehicle.isEvent


class HalloweenSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        roster = self._entity.getRoster()
        pInfo = self._entity.getPlayerInfo()
        hasEmptySlots = roster.MAX_SLOTS > stats.readyCount + roster.MAX_EMPTY_SLOTS
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if hasEmptySlots or not pInfo.isReady else None


class HalloweenBattleSquadActionsValidator(RandomSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[_HalloweenBattleVehiclesValidator(entity), SPGForbiddenSquadVehiclesValidator(entity)])


class HalloweenBattleBalanceSquadActionsValidator(BalancedSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[_HalloweenBattleVehiclesValidator(entity), SPGForbiddenSquadVehiclesValidator(entity)])
