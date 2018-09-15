# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/services_config.py
__all__ = ('getClientServicesConfig',)

def getClientServicesConfig(manager):
    """ Configures services on client.
    :param manager: helpers.dependency.DependencyManager
    """
    import account_helpers
    import connection_mgr
    import gui
    import helpers
    from skeletons.connection_mgr import IConnectionManager
    manager.addInstance(IConnectionManager, connection_mgr.ConnectionManager(), finalizer='fini')
    manager.addConfig(account_helpers.getAccountHelpersConfig)
    manager.addConfig(gui.getGuiServicesConfig)
    manager.addConfig(helpers.getHelperServicesConfig)
