# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/feature/comp7_modifiers_data_provider.py
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from comp7.constants import COMP7_SEASON_MODIFIERS_DOMAIN

class Comp7ModifiersDataProvider(ModifiersDataProvider):

    def _readClientDomain(self, modifier):
        return COMP7_SEASON_MODIFIERS_DOMAIN
