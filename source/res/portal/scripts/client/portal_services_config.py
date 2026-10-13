# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_services_config.py
import logging
from skeletons.gui.game_control import IGameStateTracker
__all__ = ('updateServicesConfig',)
_logger = logging.getLogger(__name__)

def updateServicesConfig(manager):
    from portal.skeletons.portal_event_controller import IPortalEventController
    from portal.gui.portal_event_control.portal_event_controller import PortalEventController
    from portal.gui.portal_event_control.portal_battle_results import PortalBattleResultsService
    from skeletons.gui.battle_results import IBattleResultsService
    controller = PortalEventController()
    tracker = manager.getService(IGameStateTracker)
    tracker.addController(controller)
    controller.init()
    manager.addInstance(IPortalEventController, controller)
    resultsService = PortalBattleResultsService()
    resultsService.init()
    manager.replaceInstance(IBattleResultsService, resultsService)
