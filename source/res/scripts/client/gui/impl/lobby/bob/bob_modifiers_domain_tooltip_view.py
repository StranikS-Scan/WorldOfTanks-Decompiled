# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bob/bob_modifiers_domain_tooltip_view.py
from battle_modifiers.gui.impl.lobby.tooltips.modifiers_domain_tooltip_view import ModifiersDomainTooltipView
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from helpers import dependency
from gui.bob.bob_constants import BOB_SEASON_MODIFIERS_DOMAIN
from skeletons.gui.game_control import IBobController

class BobModifiersDataProvider(ModifiersDataProvider):

    def _readClientDomain(self, modifier):
        return BOB_SEASON_MODIFIERS_DOMAIN


class BobModifiersDomainTooltipView(ModifiersDomainTooltipView):
    __bobController = dependency.descriptor(IBobController)

    def getModifiersDataProvider(self):
        return BobModifiersDataProvider(self.__bobController.battleModifiers)
