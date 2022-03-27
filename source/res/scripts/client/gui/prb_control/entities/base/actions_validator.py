# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/actions_validator.py
import logging
import weakref
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from helpers import dependency
from skeletons.tutorial import ITutorialLoader
from gui.shared.gui_items.Vehicle import Vehicle
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class _VehicleProxy(object):

    def __init__(self, vehicle):
        self.__vehicle = vehicle

    def isUnsuitableToQueue(self):
        state, _ = self.__vehicle.getState()
        return state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE

    def isReadyToFight(self):
        return self.__vehicle.isReadyToFight

    def isPresent(self):
        return True

    def isInBattle(self):
        return self.__vehicle.isInBattle

    def isDisabled(self):
        return self.__vehicle.isDisabled

    def isTooHeavy(self):
        return self.__vehicle.isTooHeavy

    def isCrewFull(self):
        return self.__vehicle.isCrewFull

    def isBroken(self):
        return self.__vehicle.isBroken

    def isDisabledInRoaming(self):
        return self.__vehicle.isDisabledInRoaming

    def isDisabledInPremIGR(self):
        return self.__vehicle.isDisabledInPremIGR

    def isDisabledInRent(self):
        return self.__vehicle.rentalIsOver

    def isRotationGroupLocked(self):
        return self.__vehicle.isRotationGroupLocked

    def isPremiumIGR(self):
        return self.__vehicle.isPremiumIGR

    def hasInvalidState(self, invalidStates):
        state, _ = self.__vehicle.getState()
        return state in invalidStates


class IActionsValidator(object):

    def canPlayerDoAction(self):
        raise NotImplementedError


class NotSupportedActionsValidator(IActionsValidator):

    def canPlayerDoAction(self):
        return ValidationResult(False)


class BaseActionsValidator(IActionsValidator):

    def __init__(self, entity):
        super(BaseActionsValidator, self).__init__()
        self._entity = weakref.proxy(entity)

    def canPlayerDoAction(self, ignoreEnable=False):
        return self._validate() if ignoreEnable or self._isEnabled() else None

    def _validate(self):
        return None

    def _isEnabled(self):
        return True


class BaseVehicleActionsValidator(BaseActionsValidator):

    def _validate(self, vehicles=None, invalidStates=None):
        if g_currentPreviewVehicle.isPresent():
            return ValidationResult(False, PREBATTLE_RESTRICTION.PREVIEW_VEHICLE_IS_PRESENT)
        vehiclesProxies = [ _VehicleProxy(vehicle) for vehicle in vehicles ] if vehicles else [g_currentVehicle]
        for vehicleProxy in vehiclesProxies:
            if vehicleProxy.isUnsuitableToQueue():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED)
            if vehicleProxy.hasInvalidState(invalidStates if invalidStates else ()):
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_ADDITIONAL_INVALID)
            if not vehicleProxy.isReadyToFight():
                if not vehicleProxy.isPresent():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT)
                if vehicleProxy.isInBattle() or vehicleProxy.isDisabled():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE)
                if vehicleProxy.isTooHeavy():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_TOO_HEAVY)
                if not vehicleProxy.isCrewFull():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.CREW_NOT_FULL)
                if vehicleProxy.isBroken():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_BROKEN)
                if vehicleProxy.isDisabledInRoaming():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_ROAMING)
                if vehicleProxy.isDisabledInPremIGR():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IN_PREMIUM_IGR_ONLY)
                if vehicleProxy.isDisabledInRent():
                    if vehicleProxy.isPremiumIGR():
                        return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IGR_RENTALS_IS_OVER)
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_RENTALS_IS_OVER)
                if vehicleProxy.isRotationGroupLocked():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_ROTATION_GROUP_LOCKED)

        return super(BaseVehicleActionsValidator, self)._validate()


class TutorialActionsValidator(BaseActionsValidator):
    __tutorialLoader = dependency.descriptor(ITutorialLoader)

    def _validate(self):
        tutorial = self.__tutorialLoader.tutorial
        return ValidationResult(False, PREBATTLE_RESTRICTION.TUTORIAL_NOT_FINISHED) if tutorial is not None and not tutorial.isAllowedToFight() else super(TutorialActionsValidator, self)._validate()


class ActionsValidatorComposite(BaseActionsValidator):

    def __init__(self, entity, validators=None, warnings=None):
        super(ActionsValidatorComposite, self).__init__(entity)
        self.__validators = validators or []
        self.__warnings = warnings or []

    def addValidator(self, validator):
        if isinstance(validator, IActionsValidator):
            self.__validators.append(validator)
        else:
            _logger.error('Validator should extends IActionsValidator: %r', validator)

    def removeValidator(self, validator):
        self.__validators.remove(validator)

    def addWarning(self, warning):
        if isinstance(warning, IActionsValidator):
            self.__warnings.append(warning)
        else:
            _logger.error('Warning object should extends IActionsValidator: %r', warning)

    def removeWarning(self, warning):
        self.__warnings.remove(warning)

    def _validate(self):
        for validator in self.__validators:
            result = validator.canPlayerDoAction()
            if result is not None:
                return result

        for warning in self.__warnings:
            result = warning.canPlayerDoAction()
            if result is not None:
                if not result.isValid:
                    raise SoftException('Warnings could not be invalid!')
                return result

        return super(ActionsValidatorComposite, self)._validate()
