# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_1vs1_battles/pre_queue/actions_validator.py
from constants import ARENA_BONUS_TYPE
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator, BaseVehicleActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from gui.periodic_battles.prb_control.actions_validator import PrimeTimeValidator
from gui.rts_battles.rts_helpers import playedRandomBattleOnTierXVehicle
from gui.prb_control.entities.rts_battles.pre_queue.actions_validator import RTSSubmodeBreakerValidator
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen import R

class RTSPrimeTimeValidator(PrimeTimeValidator):
    _controller = dependency.descriptor(IRTSBattlesController)


class RTS1x1CurrencyValidator(BaseActionsValidator):
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def _validate(self):
        return ValidationResult(False, PREBATTLE_RESTRICTION.RTS_NOT_ENOUGH_CURRENCY, None) if self.__rtsController.isCommander() and not self.__rtsController.hasEnoughCurrency(ARENA_BONUS_TYPE.RTS_1x1) else super(RTS1x1CurrencyValidator, self)._validate()


class RTS1x1RosterValidator(BaseVehicleActionsValidator):
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
        return self.__rtsController.getRoster(ARENA_BONUS_TYPE.RTS_1x1)


class RTS1x1VehicleValidator(BaseVehicleActionsValidator):
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def _validate(self, vehicles=None, invalidStates=None):
        return None


class RTS1x1BattleValidator(BaseActionsValidator):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def _validate(self):
        return ValidationResult(False, PREBATTLE_RESTRICTION.RTS_NOT_ELIGIBLE, None) if not playedRandomBattleOnTierXVehicle(self.__itemsCache, self.__rtsController) else None


class RTS1x1ActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(RTS1x1ActionsValidator, self)._createStateValidator(entity)
        validators = [baseValidator,
         RTSSubmodeBreakerValidator(entity),
         RTSPrimeTimeValidator(entity),
         RTS1x1CurrencyValidator(entity),
         RTS1x1RosterValidator(entity),
         RTS1x1BattleValidator(entity)]
        return ActionsValidatorComposite(entity, validators)

    def _createVehiclesValidator(self, entity):
        return RTS1x1VehicleValidator(entity)
