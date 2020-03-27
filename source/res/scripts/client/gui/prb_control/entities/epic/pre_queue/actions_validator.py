# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, PREBATTLE_RESTRICTION
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicVehicleValidator(BaseActionsValidator):

    def _validate(self):
        lobbyContext = dependency.instance(ILobbyContext)
        vehicle = g_currentVehicle.item
        config = lobbyContext.getServerSettings().epicBattles
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_LEVEL, {'levels': config.validVehicleLevels}) if vehicle.level not in config.validVehicleLevels else super(EpicVehicleValidator, self)._validate()


class EpicActionsValidator(PreQueueActionsValidator):

    def __init__(self, entity):
        self.__epicVehicleValidator = EpicVehicleValidator(entity)
        super(EpicActionsValidator, self).__init__(entity)

    def _createVehiclesValidator(self, entity):
        baseValidator = super(EpicActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, self.__epicVehicleValidator])

    def _validate(self):
        result = super(EpicActionsValidator, self)._validate()
        epicCtrl = dependency.instance(IEpicBattleMetaGameController)
        if not epicCtrl.isActive():
            result = ValidationResult(False, PREBATTLE_RESTRICTION.UNDEFINED)
        if result and result.restriction == PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED:
            epicValidationResult = self.__epicVehicleValidator.canPlayerDoAction()
            if epicValidationResult and not epicValidationResult.isValid:
                result = epicValidationResult
        return result
