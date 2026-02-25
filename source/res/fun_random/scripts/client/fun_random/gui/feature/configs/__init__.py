# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/configs/__init__.py
from __future__ import absolute_import
from fun_random.gui.feature.configs.providers.fun_mode_configuration import FunModeConfigurationProvider
from fun_random.gui.feature.configs.providers.fun_sub_mode_configuration import FunSubModeConfigurationProvider

def initConfigurationsCache():
    FunModeConfigurationProvider.initConfigurationsCache()
    FunSubModeConfigurationProvider.initConfigurationsCache()
