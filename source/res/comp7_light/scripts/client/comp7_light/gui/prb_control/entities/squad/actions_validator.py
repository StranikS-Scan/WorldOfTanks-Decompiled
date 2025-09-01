# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/squad/actions_validator.py
import typing
from comp7_light_constants import BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7_LIGHT
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitSlotsValidator, CommanderValidator, UnitPlayerValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController, IPlatoonController
from gui.periodic_battles.models import PrimeTimeStatus
from constants import IS_DEVELOPMENT
if typing.TYPE_CHECKING:
    from gui.prb_control.items import PlayerUnitInfo

class _Comp7LightVehiclesValidator(SquadVehiclesValidator):
    _BATTLE_MODE_VEHICLE_TAGS = BATTLE_MODE_VEH_TAGS_EXCEPT_COMP7_LIGHT


class _UnitSlotsValidator(UnitSlotsValidator):

    def _validate(self):
        stats = self._entity.getStats()
        return ValidationResult(False, UNIT_RESTRICTION.UNIT_NOT_FULL) if stats.freeSlotsCount > 0 else super(_UnitSlotsValidator, self)._validate()


class _PrimeTimeValidator(CommanderValidator):

    def _validate(self):
        status, _, _ = dependency.instance(IComp7LightController).getPrimeTimeStatus()
        return ValidationResult(False, UNIT_RESTRICTION.CURFEW) if status != PrimeTimeStatus.AVAILABLE else super(_PrimeTimeValidator, self)._validate()


class _Comp7LightPlayerValidator(UnitPlayerValidator):
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __platoonController = dependency.descriptor(IPlatoonController)

    def _validate(self):
        return ValidationResult(False, UNIT_RESTRICTION.BAN_IS_SET, None) if self.__comp7LightController.isBanned else super(_Comp7LightPlayerValidator, self)._validate()


class _Comp7LightModeStatusValidator(BaseActionsValidator):

    def _validate(self):
        if self._entity.isCommander():
            for pInfo in self._entity.getMembers().itervalues():
                if self.__isModeOfflineForPlayer(pInfo):
                    return ValidationResult(False, UNIT_RESTRICTION.MODE_OFFLINE)

        else:
            pInfo = self._entity.getPlayerInfo()
            if self.__isModeOfflineForPlayer(pInfo):
                return ValidationResult(False, UNIT_RESTRICTION.MODE_OFFLINE)
        return super(_Comp7LightModeStatusValidator, self)._validate()

    @staticmethod
    def __isModeOfflineForPlayer(pInfo):
        comp7LightEnqueueData = pInfo.extraData.get('comp7LightEnqueueData', {})
        isOnline = bool(comp7LightEnqueueData.get('isOnline', True))
        return not isOnline


class _Comp7LightSlotValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class Comp7LightSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        validators = [_Comp7LightVehiclesValidator(entity), _PrimeTimeValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)

    def _createSlotsValidator(self, entity):
        baseValidator = super(Comp7LightSquadActionsValidator, self)._createSlotsValidator(entity)
        validators = [baseValidator, _Comp7LightSlotValidator(entity)]
        if not IS_DEVELOPMENT:
            validators.append(_UnitSlotsValidator(entity))
        return ActionsValidatorComposite(entity, validators=validators)

    def _createPlayerValidator(self, entity):
        validators = [_Comp7LightPlayerValidator(entity), _Comp7LightModeStatusValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)
