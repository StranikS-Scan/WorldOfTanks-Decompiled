# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/prb_control/entities/epic/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_EPIC
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitStateValidator
from gui.prb_control.entities.random.squad.actions_validator import BalancedSquadVehiclesValidator, RoleForbiddenSquadVehiclesValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import time_utils, dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class _EpicVehiclesValidator(SquadVehiclesValidator):
    _BATTLE_MODE_VEHICLE_TAGS = BATTLE_MODE_VEH_TAGS_EXCEPT_EPIC


class _EpicBalancedSquadVehiclesValidator(BalancedSquadVehiclesValidator):
    __epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def _validate(self):
        availableLevels = self.__epicCtrl.getSuitableForQueueVehicleLevels()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL) if not pInfo.isReady and g_currentVehicle.isPresent() and g_currentVehicle.item.level not in availableLevels else super(_EpicBalancedSquadVehiclesValidator, self)._validate()


class _EpicStateValidator(UnitStateValidator):
    __epicCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def _validate(self):
        currentSeason = self.__epicCtrl.getCurrentSeason()
        if currentSeason:
            if currentSeason.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                return super(_EpicStateValidator, self)._validate()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_INACTIVE_PERIPHERY_UNDEF)


class EpicSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return ActionsValidatorComposite(entity, validators=[_EpicBalancedSquadVehiclesValidator(entity), _EpicVehiclesValidator(entity), RoleForbiddenSquadVehiclesValidator(entity)])

    def _createStateValidator(self, entity):
        return _EpicStateValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(EpicSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, EpicSquadSlotsValidator(entity)])


class EpicSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None
