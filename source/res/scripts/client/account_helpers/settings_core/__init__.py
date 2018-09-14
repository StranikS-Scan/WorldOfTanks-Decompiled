# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/__init__.py
from account_helpers.settings_core.SettingsCache import SettingsCache
from account_helpers.settings_core.SettingsCore import SettingsCore
from skeletons.account_helpers.settings_core import ISettingsCache, ISettingsCore

def getSettingsCoreConfig(manager):
    """ Configures services for package gui.
    :param manager: helpers.dependency.DependencyManager
    """
    cache = SettingsCache()
    manager.addInstance(ISettingsCache, cache, finalizer='fini')
    core = SettingsCore()
    manager.addInstance(ISettingsCore, core, finalizer='fini')
    cache.init()
    core.init()
