# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/actions_validator.py
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.entities.base.actions_validator import CurrentVehicleActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, PREBATTLE_RESTRICTION as restrictions
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IWhiteTigerController
from wt_settings import g_wt_config

class WhiteTigerCurrentVehicleActionsValidator(CurrentVehicleActionsValidator):
    __wtController = dependency.descriptor(IWhiteTigerController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def _validate(self):
        vehicle = self.__prebattleVehicle.item
        if not vehicle:
            return ValidationResult(False, restrictions.VEHICLE_NOT_PRESENT)
        elif vehicle.isInBattle or vehicle.isDisabled:
            return ValidationResult(False, restrictions.VEHICLE_IN_BATTLE)
        elif vehicle.isUnsuitableToQueue:
            return ValidationResult(False, restrictions.VEHICLE_NOT_SUPPORTED)
        elif not g_wt_config.hasTokensForBattle(vehicle.intCD):
            isSpecialBoss = g_wt_config.isSpecialBossVehicle(vehicle.intCD)
            return ValidationResult(False, restrictions.GOLD_TICKETS_SHORTAGE if isSpecialBoss else restrictions.TICKETS_SHORTAGE)
        else:
            return None


class WhiteTigerBattleActionsValidator(PreQueueActionsValidator):
    __wtController = dependency.descriptor(IWhiteTigerController)

    def _validate(self):
        status, _, _ = self.__wtController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE) if status != PrimeTimeStatus.AVAILABLE else super(WhiteTigerBattleActionsValidator, self)._validate()

    def _createVehiclesValidator(self, entity):
        return WhiteTigerCurrentVehicleActionsValidator(entity)
