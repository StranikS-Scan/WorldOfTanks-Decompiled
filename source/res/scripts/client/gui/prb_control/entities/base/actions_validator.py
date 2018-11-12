# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/actions_validator.py
import logging
import weakref
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION
import tutorial.loader as tutorialLoader
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

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


class CurrentVehicleActionsValidator(BaseActionsValidator):

    def _validate(self):
        if g_currentPreviewVehicle.isPresent():
            return ValidationResult(False, PREBATTLE_RESTRICTION.PREVIEW_VEHICLE_IS_PRESENT)
        if not g_currentVehicle.isReadyToFight():
            if not g_currentVehicle.isPresent():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT)
            if g_currentVehicle.isInBattle():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE)
            if not g_currentVehicle.isCrewFull():
                return ValidationResult(False, PREBATTLE_RESTRICTION.CREW_NOT_FULL)
            if g_currentVehicle.isBroken():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_BROKEN)
            if g_currentVehicle.isDisabledInRoaming():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_ROAMING)
            if g_currentVehicle.isDisabledInPremIGR():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IN_PREMIUM_IGR_ONLY)
            if g_currentVehicle.isDisabledInRent():
                if g_currentVehicle.isPremiumIGR():
                    return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_IGR_RENTALS_IS_OVER)
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_RENTALS_IS_OVER)
            if g_currentVehicle.isRotationGroupLocked():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_ROTATION_GROUP_LOCKED)
        return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED) if g_currentVehicle.isUnsuitableToQueue() else super(CurrentVehicleActionsValidator, self)._validate()


class TutorialActionsValidator(BaseActionsValidator):

    def _validate(self):
        if tutorialLoader.g_loader is not None:
            tutorial = tutorialLoader.g_loader.tutorial
            if tutorial is not None and not tutorial.isAllowedToFight():
                return ValidationResult(False, PREBATTLE_RESTRICTION.TUTORIAL_NOT_FINISHED)
        return super(TutorialActionsValidator, self)._validate()


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
