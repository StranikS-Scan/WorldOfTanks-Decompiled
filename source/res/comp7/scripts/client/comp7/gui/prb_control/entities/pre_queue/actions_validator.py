# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/prb_control/entities/pre_queue/actions_validator.py
import typing
from CurrentVehicle import g_currentVehicle
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import getSeasonNameEnum
from gui.periodic_battles.models import PeriodType
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.entity import BasePrbEntity

class Comp7TournamentValidator(BaseActionsValidator):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def _validate(self):
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_NOT_ENOUGH_SUITABLE_VEHICLES) if not self.__comp7Controller.hasEnoughReadyToFightVehicles() else None


class Comp7Validator(BaseActionsValidator):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _validate(self):
        if self.__comp7Ctrl.isBanned:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.BAN_IS_SET)
        if not self.__comp7Ctrl.hasSuitableVehicles():
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_NO_SUITABLE_VEHICLES, ctx={'levels': self.__comp7Ctrl.getModeSettings().levels})
        if not self.__comp7Ctrl.hasEnoughReadyToFightVehicles():
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_NOT_ENOUGH_SUITABLE_VEHICLES, ctx={'amount': self.__comp7Ctrl.getModeSettings().minVehiclesRequired})
        if self.__comp7Ctrl.isInPreannounceState():
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_IS_IN_PREANNOUNCE)
        periodInfo = self.__comp7Ctrl.getPeriodInfo()
        if periodInfo.periodType in (PeriodType.AFTER_SEASON,
         PeriodType.AFTER_CYCLE,
         PeriodType.BETWEEN_SEASONS,
         PeriodType.ALL_NOT_AVAILABLE_END,
         PeriodType.STANDALONE_NOT_AVAILABLE_END):
            season = getSeasonNameEnum(self.__comp7Ctrl, SeasonName).value
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_SEASON_ENDED, ctx={'season': season})
        if self.__comp7Ctrl.isQualificationResultsProcessing() or self.__comp7Ctrl.isQualificationCalculationRating():
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.QUALIFICATION_RESULTS_PROCESSING)
        if not self.__comp7Ctrl.isInPrimeTime():
            if self.__comp7Ctrl.hasAvailablePrimeTimeServers():
                return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_OFFLINE) if self.__comp7Ctrl.isOffline else super(Comp7Validator, self)._validate()


class Comp7VehicleValidator(BaseActionsValidator):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _validate(self):
        return None if not g_currentVehicle.isPresent() else self.__comp7Ctrl.isSuitableVehicle(g_currentVehicle.item)


class Comp7ActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(Comp7ActionsValidator, self)._createStateValidator(entity)
        validators = [baseValidator, Comp7Validator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)

    def _createVehiclesValidator(self, entity):
        baseValidator = super(Comp7ActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [Comp7VehicleValidator(entity), baseValidator])
