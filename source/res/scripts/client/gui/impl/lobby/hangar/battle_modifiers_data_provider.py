# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/battle_modifiers_data_provider.py
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from helpers import dependency
from skeletons.gui.game_control import IBattleModifiersController

class BattleModifiersDataProvider(ModifiersDataProvider):
    _battleModifiersController = dependency.descriptor(IBattleModifiersController)

    def _readClientDomain(self, modifier):
        return self._battleModifiersController.getCurrentDomain()
