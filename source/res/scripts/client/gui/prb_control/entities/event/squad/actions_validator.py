# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from constants import QUEUE_TYPE
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.entities.random.squad.actions_validator import RandomSquadActionsValidator, SPGForbiddenSquadVehiclesValidator, BalancedSquadActionsValidator
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.prb_control.items import ValidationResult

class _EventBattleVehiclesValidator(SquadVehiclesValidator):

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
                if commanderQueueType == QUEUE_TYPE.EVENT_BATTLES and vehicle.isWheeledTech or commanderQueueType == QUEUE_TYPE.EVENT_BATTLES_2 and not vehicle.isWheeledTech:
                    return ValidationResult(False, UNIT_RESTRICTION.UNSUITABLE_VEHICLE)

        return super(_EventBattleVehiclesValidator, self)._validate()

    def _isValidMode(self, vehicle):
        return super(_EventBattleVehiclesValidator, self)._isValidMode(vehicle) or vehicle.isEvent


class EventSquadSlotsValidator(CommanderValidator):
    pass


class EventBattleSquadActionsValidator(RandomSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[_EventBattleVehiclesValidator(entity), SPGForbiddenSquadVehiclesValidator(entity)])


class EventBattleBalanceSquadActionsValidator(BalancedSquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[_EventBattleVehiclesValidator(entity), SPGForbiddenSquadVehiclesValidator(entity)])
