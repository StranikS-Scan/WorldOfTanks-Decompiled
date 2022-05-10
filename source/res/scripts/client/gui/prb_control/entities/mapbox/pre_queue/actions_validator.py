# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/mapbox/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite, CurrentVehicleActionsValidator
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, UNIT_RESTRICTION
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IMapboxController

class MapboxVehicleValidator(CurrentVehicleActionsValidator):

    def _validate(self):
        vehicle = g_currentVehicle.item
        result = self.validateForMapbox(vehicle)
        return result if result is not None else super(MapboxVehicleValidator, self)._validate()

    @staticmethod
    def validateForMapbox(vehicle):
        if vehicle is None:
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_SELECTED)
        lobbyContext = dependency.instance(ILobbyContext)
        config = lobbyContext.getServerSettings().mapbox
        if vehicle.level not in config.levels:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_LEVEL, {'levels': config.levels})
        elif vehicle.intCD in config.forbiddenVehTypes:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE, {'forbiddenType': vehicle.shortUserName})
        else:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_CLASS, {'forbiddenClass': vehicle.type}) if vehicle.type in config.forbiddenClassTags else None


class MapboxStateValidator(BaseActionsValidator):

    def _validate(self):
        mapboxController = dependency.instance(IMapboxController)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE) if not mapboxController.isActive() or not mapboxController.isInPrimeTime() else super(MapboxStateValidator, self)._validate()


class MapboxActionsValidator(PreQueueActionsValidator):

    def _createVehiclesValidator(self, entity):
        baseValidator = super(MapboxActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [MapboxVehicleValidator(entity), baseValidator])

    def _createStateValidator(self, entity):
        baseValidator = super(MapboxActionsValidator, self)._createStateValidator(entity)
        return ActionsValidatorComposite(entity, [baseValidator, MapboxStateValidator(entity)])
