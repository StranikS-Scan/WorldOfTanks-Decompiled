# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/services_config.py
__all__ = ('getClientServicesConfig',)

def getClientServicesConfig(manager):
    import account_helpers
    import connection_mgr
    import MapActivities
    import gui
    import gameplay
    import helpers
    import festivity
    from skeletons.connection_mgr import IConnectionManager
    from skeletons.map_activities import IMapActivities
    manager.addInstance(IConnectionManager, connection_mgr.ConnectionManager(), finalizer='fini')
    manager.addInstance(IMapActivities, MapActivities.MapActivities(), finalizer='destroy')
    manager.addConfig(account_helpers.getAccountHelpersConfig)
    manager.addConfig(gameplay.getGameplayConfig)
    manager.addConfig(festivity.getFestivityConfig)
    manager.addConfig(gui.getGuiServicesConfig)
    manager.addConfig(helpers.getHelperServicesConfig)
