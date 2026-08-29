# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/services_config.py
import logging
__all__ = ('getClientServicesConfig',)
_logger = logging.getLogger(__name__)

def getOfflineClientServicesConfig(manager):
    import connection_mgr
    from skeletons.connection_mgr import IConnectionManager
    manager.addInstance(IConnectionManager, connection_mgr.ConnectionManager(), finalizer='fini')


def getClientServicesConfig(manager):
    import account_helpers
    import connection_mgr
    import MapActivities
    import dyn_objects_cache
    import gui
    import gameplay
    import helpers
    import uilogging
    import festivity
    import AvatarInputHandler
    from vehicle_systems.appearance_cache import AppearanceCache
    from skeletons.connection_mgr import IConnectionManager
    from skeletons.map_activities import IMapActivities
    from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
    from skeletons.vehicle_appearance_cache import IAppearanceCache
    import prebattle_vehicle
    from skeletons.prebattle_vehicle import IPrebattleVehicle
    manager.addInstance(IConnectionManager, connection_mgr.ConnectionManager(), finalizer='fini')
    manager.addInstance(IMapActivities, MapActivities.MapActivities(), finalizer='destroy')
    manager.addInstance(IBattleDynamicObjectsCache, dyn_objects_cache.BattleDynamicObjectsCache(), finalizer='destroy')
    manager.addInstance(IAppearanceCache, AppearanceCache(), finalizer='clear')
    manager.addInstance(IPrebattleVehicle, prebattle_vehicle.PrebattleVehicle(), finalizer='fini')
    manager.addConfig(account_helpers.getAccountHelpersConfig)
    manager.addConfig(gameplay.getGameplayConfig)
    manager.addConfig(festivity.getFestivityConfig)
    manager.addConfig(gui.getGuiServicesConfig)
    manager.addConfig(uilogging.getUILoggingConfig)
    manager.addConfig(helpers.getHelperServicesConfig)
    manager.addConfig(AvatarInputHandler.getAvatarInputHandlerConfig)
    from gui import GUI_SETTINGS
    if GUI_SETTINGS.isGuiEnabled():
        try:
            import tutorial
        except ImportError:
            _logger.exception('Module tutorial not found')
            from helpers import tutorial

    else:
        from helpers import tutorial
    manager.addConfig(tutorial.getTutorialConfig)
