# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/basic_missions_tab.py
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from helpers import dependency
import constants
from gui.impl.gen import R
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.server_events.events_helpers import isWeeklyQuestsEnable
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.basic_missions_tab_model import BasicMissionsTabModel
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.daily_missions_section_presenter import DailyMissionsSectionPresenter
from gui.impl.lobby.user_missions.hub.tabs.basic.weekly_missions import WeeklyMissions
from gui.impl.lobby.user_missions.hub.update_children_mixin import UpdateChildrenMixin
from gui.impl.pub.view_component import ViewComponent
from gui.impl.lobby.user_missions.hub.tabs.basic.personal_missions import PersonalMissionsPresenter

class BasicMissionsTab(UpdateChildrenMixin, ViewComponent[BasicMissionsTabModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.MainView()
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, targetQuestId):
        self._targetQuestId = targetQuestId
        self.personalMissionsCache = self.eventsCache.getPersonalMissions()
        super(BasicMissionsTab, self).__init__(model=BasicMissionsTabModel)

    @property
    def viewModel(self):
        return super(BasicMissionsTab, self).getViewModel()

    def _getChildComponents(self):
        return {DailyMissionsSectionPresenter.LAYOUT_ID: lambda : DailyMissionsSectionPresenter(self._targetQuestId),
         WeeklyMissions.LAYOUT_ID: WeeklyMissions,
         PersonalMissionsPresenter.LAYOUT_ID: PersonalMissionsPresenter}

    def _onLoaded(self, *args, **kwargs):
        super(BasicMissionsTab, self)._onLoaded()
        self._updateDailyBlockStatus()
        self.__updatePersonalMissionSection()

    def _getEvents(self):
        return ((g_playerEvents.onConfigModelUpdated, self.__onConfigModelUpdated), (self.eventsCache.onSyncCompleted, self.__onCacheSyncCompleted), (self.itemsCache.onSyncCompleted, self.__onInventoryCacheSyncCompleted))

    def _updateDailyBlockStatus(self):
        self.viewModel.setIsDailySectionAvailable(umgConfigSchema.getModel().enableAllDaily)
        self.viewModel.setIsWeeklySectionAvailable(umgConfigSchema.getModel().enableAllWeekly and isWeeklyQuestsEnable())

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            self._updateDailyBlockStatus()

    def __updatePersonalMissionSection(self):
        self.viewModel.setIsPMSectionAvailable(self.__hasRequiredVehicle() and not self.__isCampaignPaused() and not self.__isCampaignCompleted())

    def __onCacheSyncCompleted(self):
        self.__updatePersonalMissionSection()

    def __onInventoryCacheSyncCompleted(self, reason, _):
        if reason == CACHE_SYNC_REASON.INVENTORY_RESYNC:
            self.__updatePersonalMissionSection()

    def __hasRequiredVehicle(self):
        vehicleCriteria = REQ_CRITERIA.IN_OWNERSHIP | REQ_CRITERIA.VEHICLE.LEVELS(range(6, constants.MAX_VEHICLE_LEVEL + 1))
        return len(self.itemsCache.items.getVehicles(vehicleCriteria)) > 0

    def __isCampaignCompleted(self):
        campaignOperations = self.personalMissionsCache.getOperationsForBranch('pm3')
        return all((op.isFullCompleted() for op in campaignOperations.values()))

    def __isCampaignPaused(self):
        return False
