# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/configs/providers/fun_sub_mode_configuration.py
from __future__ import absolute_import
import typing
from fun_random.gui.feature.configs.providers.base_configuration import FunBaseConfigurationProvider
from fun_random.gui.feature.configs.sub_modes.sub_mode import funSubModeCompositeConfigurationSchema
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.configs.sub_modes.sub_mode import FunSubModeCompositeConfigurationModel
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode

class FunSubModeConfigurationProvider(FunBaseConfigurationProvider):
    _CONFIGURATION_SCHEMA = funSubModeCompositeConfigurationSchema
    _EMPTY_CONFIGURATION_PATH = 'fun_random/gui/configs/gamemodes/fun_sub_modes/fun_sub_mode_empty.xml'

    def getConfigurationModel(self):
        return self._configurationModel

    def _getRuntimeConfiguration(self, subMode, *args):
        return {'subMode': {'assetsPointer': subMode.getAssetsPointer(),
                     'pbsEfficiency': subMode.getSettings().client.postbattle.get('postbattleEfficiency', {})}}
