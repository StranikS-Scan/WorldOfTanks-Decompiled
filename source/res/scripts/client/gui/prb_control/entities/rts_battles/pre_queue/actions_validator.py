# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_battles/pre_queue/actions_validator.py
import typing
from constants import ARENA_BONUS_TYPE
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator, BaseVehicleActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION, PRE_QUEUE_RESTRICTION
from gui.periodic_battles.prb_control.actions_validator import PrimeTimeValidator
from gui.rts_battles.rts_helpers import playedRandomBattleOnTierXVehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from helpers.server_settings import RTSBattlesConfig

class RTSPrimeTimeValidator(PrimeTimeValidator):
    _controller = dependency.descriptor(IRTSBattlesController)


class RTS1x7CurrencyValidator(BaseActionsValidator):
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def _validate(self):
        return ValidationResult(False, PREBATTLE_RESTRICTION.RTS_NOT_ENOUGH_CURRENCY, None) if self.__rtsController.isCommander() and not self.__rtsController.hasEnoughCurrency(ARENA_BONUS_TYPE.RTS) else super(RTS1x7CurrencyValidator, self)._validate()


class RTS1x7VehicleValidator(BaseVehicleActionsValidator):
    __rtsController = dependency.descriptor(IRTSBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def _validate(self, vehicles=None, invalidStates=None):
        if self.__rtsController.isCommander():
            return None
        else:
            vehicleConfig = self.__rtsController.getSettings().getVehicleRestrictions(ARENA_BONUS_TYPE.RTS)
            allowedLevels = vehicleConfig.get('levels', frozenset())
            criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(allowedLevels)
            invVehicles = self.__itemsCache.items.getVehicles(criteria)
            if not invVehicles:
                return ValidationResult(False, PREBATTLE_RESTRICTION.LIMIT_VEHICLES, None)
            if g_currentVehicle.isPresent():
                vehicle = g_currentVehicle.item
                if vehicle.level not in allowedLevels:
                    return ValidationResult(False, PREBATTLE_RESTRICTION.LIMIT_LEVEL, None)
                if not vehicle.isAmmoFull:
                    return ValidationResult(False, PREBATTLE_RESTRICTION.LIMIT_AMMO, None)
            return super(RTS1x7VehicleValidator, self)._validate(vehicles, invalidStates)


class RTS1x7RosterValidator(BaseVehicleActionsValidator):
    __rtsController = dependency.descriptor(IRTSBattlesController)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def _validate(self, vehicles=None, invalidStates=None):
        if not self.__rtsController.isCommander():
            return None
        else:
            return ValidationResult(False, PREBATTLE_RESTRICTION.AI_ROSTER_NOT_SET, None) if self.hasUnsavedRosterChanges or not self.hasFilledRoster else None

    @property
    def hasUnsavedRosterChanges(self):
        rosterView = self.__guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.rts.RosterView())
        return rosterView and rosterView.hasUnsavedChanges()

    @property
    def hasFilledRoster(self):
        roster = self._getRoster()
        return all(roster.vehicles) and all(roster.supplies)

    def _getRoster(self):
        return self.__rtsController.getRoster(ARENA_BONUS_TYPE.RTS)


class RTSBattleValidator(BaseActionsValidator):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def _validate(self):
        return ValidationResult(False, PREBATTLE_RESTRICTION.RTS_NOT_ELIGIBLE, None) if not playedRandomBattleOnTierXVehicle(self.__itemsCache, self.__rtsController) else None


class RTSSubmodeBreakerValidator(BaseActionsValidator):
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def _validate(self):
        settings = self.__rtsController.getSettings()
        bonusType = self.__rtsController.getBattleMode()
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.RTS_SUBMODE_NOT_AVAILABLE, None) if not settings.isSubmodeEnabled(bonusType) else super(RTSSubmodeBreakerValidator, self)._validate()


class RTSActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(RTSActionsValidator, self)._createStateValidator(entity)
        validators = [baseValidator,
         RTSSubmodeBreakerValidator(entity),
         RTSPrimeTimeValidator(entity),
         RTS1x7CurrencyValidator(entity),
         RTS1x7RosterValidator(entity),
         RTSBattleValidator(entity)]
        return ActionsValidatorComposite(entity, validators)

    def _createVehiclesValidator(self, entity):
        return RTS1x7VehicleValidator(entity)
