# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/tooltips/event_banner_tooltip.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.halloween.tooltips.event_banner_tooltip_model import EventBannerTooltipModel
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.server_events.events_helpers import EventInfoModel
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from visual_script_client.arena_blocks import dependency

class EventBannerTooltip(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.halloween.tooltips.EventBannerTooltip())
        settings.model = EventBannerTooltipModel()
        super(EventBannerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventBannerTooltip, self).getViewModel()

    def _onLoading(self):
        super(EventBannerTooltip, self)._onLoading()
        vehiclesController = self.gameEventController.getVehiclesController()
        totalVehicles = vehiclesController.getAllVehiclesInInventory()
        dailyQuests = sum((vehiclesController.hasDailyQuest(vehCD) for vehCD in totalVehicles))
        with self.viewModel.transaction() as vm:
            vm.setAvailable(dailyQuests)
            vm.setTotal(len(totalVehicles))
            vm.setCountdownValue(EventInfoModel.getDailyProgressResetTimeDelta())
