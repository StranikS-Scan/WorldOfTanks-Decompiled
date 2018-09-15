# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/actions_validator.py
import weakref
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION

class IActionsValidator(object):
    """
    Base interface class for actions validation.
    """

    def canPlayerDoAction(self):
        """
        Can player pass all validations abstract method.
        """
        raise NotImplementedError


class NotSupportedActionsValidator(IActionsValidator):
    """
    Player cannot do any actions.
    """

    def canPlayerDoAction(self):
        return ValidationResult(False)


class BaseActionsValidator(IActionsValidator):
    """
    Base class for actions validation.
    """

    def __init__(self, entity):
        """
        Default object initialization.
        Args:
            entity: prebattle entity
        """
        super(BaseActionsValidator, self).__init__()
        self._entity = weakref.proxy(entity)

    def canPlayerDoAction(self, ignoreEnable=False):
        """
        Can player pass all validations for enabled validator.
        Args:
            ignoreEnable: override for enable check
        
        Returns:
            validation result
        """
        return self._validate() if ignoreEnable or self._isEnabled() else None

    def _validate(self):
        """
        Method that do all the job related to validation.
        Returns:
            validation result
        """
        return None

    def _isEnabled(self):
        """
        Is this validator enabled.
        """
        return True


class CurrentVehicleActionsValidator(BaseActionsValidator):
    """
    Current vehicle status validator.
    """

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
            if g_currentVehicle.isFalloutOnly():
                return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_FALLOUT_ONLY)
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
        return super(CurrentVehicleActionsValidator, self)._validate()


class ActionsValidatorComposite(BaseActionsValidator):
    """
    Validations composite.
    """

    def __init__(self, entity, validators=None, warnings=None):
        """
        Default object initialization.
        Args:
            entity: prebattle entity
            validators: validatros list
            warnings: warners list
        """
        super(ActionsValidatorComposite, self).__init__(entity)
        self.__validators = validators or []
        self.__warnings = warnings or []

    def addValidator(self, validator):
        """
        Pushes new validator.
        Args:
            validator: new validator to add
        """
        assert isinstance(validator, IActionsValidator)
        self.__validators.append(validator)

    def removeValidator(self, validator):
        """
        Removes validator from chain.
        Args:
            validator: validator to extract
        """
        self.__validators.remove(validator)

    def addWarning(self, warning):
        """
        Pushes new warning.
        Args:
            warning: new warning to add
        """
        assert isinstance(warning, IActionsValidator)
        self.__warnings.append(warning)

    def removeWarning(self, warning):
        """
        Removes warning from chain.
        Args:
            warning: warning to extract
        """
        self.__warnings.remove(warning)

    def _validate(self):
        for validator in self.__validators:
            result = validator.canPlayerDoAction()
            if result is not None:
                return result

        for warning in self.__warnings:
            result = warning.canPlayerDoAction()
            if result is not None:
                assert result.isValid, 'Warnings could not be invalid!'
                return result

        return super(ActionsValidatorComposite, self)._validate()
