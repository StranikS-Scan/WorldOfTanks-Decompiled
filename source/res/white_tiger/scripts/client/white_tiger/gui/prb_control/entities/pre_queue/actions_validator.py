# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/actions_validator.py
from gui.periodic_battles.prb_control.actions_validator import PrimeTimeValidator
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from helpers import dependency
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS

class WhiteTigerVehicleValidator(BaseActionsValidator):
    __economicsCtrl = dependency.descriptor(IEconomicsController)

    def _validate(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT, None)
        else:
            if WT_VEHICLE_TAGS.BOSS in vehicle.tags and WT_VEHICLE_TAGS.PRIORITY_BOSS not in vehicle.tags:
                if not self.__economicsCtrl.hasEnoughTickets():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_READY, ctx={'noTickets': True})
            return super(WhiteTigerVehicleValidator, self)._validate()


class WhiteTigerPrimeTimeValidator(PrimeTimeValidator):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def _getController(self):
        return self.__wtCtrl


class WhiteTigerActionsValidator(PreQueueActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(WhiteTigerActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [WhiteTigerVehicleValidator(entity), baseValidator])

    def _createStateValidator(self, entity):
        baseValidator = super(WhiteTigerActionsValidator, self)._createStateValidator(entity)
        validators = [WhiteTigerPrimeTimeValidator(entity), baseValidator]
        return ActionsValidatorComposite(entity, validators=validators)
