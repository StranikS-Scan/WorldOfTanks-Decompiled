# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_modes/equalization_sub_mode.py
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from fun_random.gui.feature.sub_modes.base_sub_mode import FunBaseSubMode
EQUALIZATION = 'equalization'

class EqualizationModifiersDataProvider(ModifiersDataProvider):

    def getDomains(self):
        return (EQUALIZATION,) + super(EqualizationModifiersDataProvider, self).getDomains()


class FunEqualizationSubMode(FunBaseSubMode):

    def _getModifiersDataProvider(self, subModeSettings):
        return EqualizationModifiersDataProvider(subModeSettings.client.battleModifiersDescr)
