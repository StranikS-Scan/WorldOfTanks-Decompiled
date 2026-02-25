# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/__init__.py
from __future__ import absolute_import
from fun_random.gui.feature.configs import initConfigurationsCache
from fun_random.gui.feature.sub_modes import registerFunRandomSubModes

def registerFunRandomFeature():
    initConfigurationsCache()
    registerFunRandomSubModes()
