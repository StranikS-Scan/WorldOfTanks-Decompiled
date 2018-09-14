# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/services_config.py
import account_helpers
import gui
__all__ = ('getClientServicesConfig',)

def getClientServicesConfig(manager):
    """ Configures services for package gui.
    :param manager: helpers.dependency.DependencyManager
    """
    manager.install(gui.getGuiServicesConfig)
    manager.install(account_helpers.getAccountHelpersConfig)
