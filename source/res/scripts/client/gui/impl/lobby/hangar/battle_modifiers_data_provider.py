# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/battle_modifiers_data_provider.py
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from gui.impl.lobby.stronghold.stronghold_helpers import getBattleModifiersDomain

class BattleModifiersDataProvider(ModifiersDataProvider):

    def _readClientDomain(self, modifier):
        return getBattleModifiersDomain()
