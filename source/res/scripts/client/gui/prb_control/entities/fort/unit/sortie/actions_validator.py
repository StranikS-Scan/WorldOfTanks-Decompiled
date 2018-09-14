# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/sortie/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.unit.actions_validator import UnitActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class SortiePlayerValidator(BaseActionsValidator):
    """
    Sortie player validation
    """

    def _validate(self):
        from gui.shared.ClanCache import g_clanCache
        from gui.LobbyContext import g_lobbyContext
        if not g_lobbyContext.getServerSettings().isFortsEnabled():
            return ValidationResult(False, UNIT_RESTRICTION.FORT_DISABLED)
        provider = g_clanCache.fortProvider
        if provider:
            controller = provider.getController()
            if controller:
                sortiesHoursCtrl = controller.getSortiesCurfewCtrl()
                if sortiesHoursCtrl:
                    availableAtThisTime, availableAtCurrServer = sortiesHoursCtrl.getStatus()
                    if not availableAtThisTime or not availableAtCurrServer:
                        return ValidationResult(False, UNIT_RESTRICTION.CURFEW)
        return super(SortiePlayerValidator, self)._validate()


class SortieActionsValidator(UnitActionsValidator):
    """
    Sortie actions validation class
    """

    def _createPlayerValidator(self, entity):
        baseValidator = super(SortieActionsValidator, self)._createPlayerValidator(entity)
        return ActionsValidatorComposite(entity, validators=[SortiePlayerValidator(entity), baseValidator])
