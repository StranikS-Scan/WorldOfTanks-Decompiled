# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/battle_modifiers_domain_tooltip_view.py
from battle_modifiers.gui.impl.lobby.tooltips.modifiers_domain_tooltip_view import ModifiersDomainTooltipView
from gui.impl.lobby.hangar.battle_modifiers_data_provider import BattleModifiersDataProvider
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IBattleModifiersController

class BattleModifiersDomainTooltipView(ModifiersDomainTooltipView, IGlobalListener):
    __battleModifiersController = dependency.descriptor(IBattleModifiersController)

    def getModifiersDataProvider(self):
        modifiers = self.__battleModifiersController.battleModifiers
        return BattleModifiersDataProvider(modifiers)
