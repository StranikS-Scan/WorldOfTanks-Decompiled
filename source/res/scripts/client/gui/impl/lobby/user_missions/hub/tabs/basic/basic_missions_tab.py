# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/basic_missions_tab.py
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getSuitableVehicles
from gui.server_events.pm_constants import IS_PM3_QUEST_ENABLED, DISABLED_PM_OPERATIONS
from helpers import dependency
from gui.impl.gen import R
from personal_missions import PM_BRANCH
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.server_events.events_helpers import isWeeklyQuestsEnable
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.basic_missions_tab_model import BasicMissionsTabModel
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.daily_missions_section_presenter import DailyMissionsSectionPresenter
from gui.impl.lobby.user_missions.hub.tabs.basic.weekly_missions import WeeklyMissions
from gui.impl.lobby.user_missions.hub.update_children_mixin import UpdateChildrenMixin
from gui.impl.pub.view_component import ViewComponent
from gui.impl.lobby.user_missions.hub.tabs.basic.personal_missions_widget import PersonalMissionsWindgetPresenter

class BasicMissionsTab(UpdateChildrenMixin, ViewComponent[BasicMissionsTabModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.MainView()
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, targetQuestId):
        self._targetQuestId = targetQuestId
        self._hasSuitableVehicles = False
        self.__personalMissions = self.eventsCache.getPersonalMissions()
        self.__pm3Operations = self.__personalMissions.getAllOperations(PM_BRANCH.V2_BRANCHES)
        super(BasicMissionsTab, self).__init__(model=BasicMissionsTabModel)

    @property
    def viewModel(self):
        return super(BasicMissionsTab, self).getViewModel()

    def _getChildComponents(self):
        return {DailyMissionsSectionPresenter.LAYOUT_ID: lambda : DailyMissionsSectionPresenter(self._targetQuestId),
         WeeklyMissions.LAYOUT_ID: WeeklyMissions,
         PersonalMissionsWindgetPresenter.LAYOUT_ID: PersonalMissionsWindgetPresenter}

    def _onLoaded(self, *args, **kwargs):
        super(BasicMissionsTab, self)._onLoaded()
        self._hasSuitableVehicles = bool(getSuitableVehicles())
        self._updateDailyBlockStatus()
        self.__updatePersonalMissionSection()

    def _getCallbacks(self):
        return super(BasicMissionsTab, self)._getCallbacks() + (('inventory.1.compDescr', self.__onVehiclesInventorySyncCompleted),)

    def _getEvents(self):
        return ((g_playerEvents.onConfigModelUpdated, self.__onConfigModelUpdated),
         (self.eventsCache.onPMSyncCompleted, self.__onCacheSyncCompleted),
         (self.itemsCache.onSyncCompleted, self.__onInventoryCacheSyncCompleted),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _updateDailyBlockStatus(self):
        self.viewModel.setIsDailySectionAvailable(umgConfigSchema.getModel().enableAllDaily)
        self.viewModel.setIsWeeklySectionAvailable(umgConfigSchema.getModel().enableAllWeekly and isWeeklyQuestsEnable())

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if IS_PM3_QUEST_ENABLED in diff or DISABLED_PM_OPERATIONS in diff:
            inProgressOperations = self.eventsCache.getPersonalMissions().getActiveOperations(PM_BRANCH.V2_BRANCHES)
            inProgressOperationsIDs = [ operation.getID() for operation in inProgressOperations ]
            if not diff.get(IS_PM3_QUEST_ENABLED, True) or inProgressOperationsIDs & diff.get(DISABLED_PM_OPERATIONS, {}).keys():
                self.viewModel.setIsPMSectionAvailable(False)
            else:
                self.__updatePersonalMissionSection()

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            self._updateDailyBlockStatus()

    def __updatePersonalMissionSection(self):
        self.viewModel.setIsPMSectionAvailable(self.__isPM3Enabled() and not self.__isPMOperationDisabled() and not self.__isCampaignCompleted() and (self.__isPM3Active() or (self._hasSuitableVehicles or self.__isPM12Active()) and not self.__isCampaignStarted()))

    def __onCacheSyncCompleted(self, *_):
        self.__updatePersonalMissionSection()

    def __onInventoryCacheSyncCompleted(self, reason, _):
        if reason == CACHE_SYNC_REASON.INVENTORY_RESYNC:
            self.__updatePersonalMissionSection()

    def __onVehiclesInventorySyncCompleted(self, _):
        self._hasSuitableVehicles = bool(getSuitableVehicles())
        self.__updatePersonalMissionSection()

    def __isCampaignCompleted(self):
        return all([ operation.isFullCompleted() for operation in self.__pm3Operations.values() ])

    def __isCampaignStarted(self):
        return self.__personalMissions.isPM3Activated()

    def __isPM3Enabled(self):
        return self.lobbyContext.getServerSettings().isPersonalMissionsEnabled(PM_BRANCH.PERSONAL_MISSION_3)

    def __isPMOperationDisabled(self):
        return self.__personalMissions.isActiveOperationDisabled(PM_BRANCH.V2_BRANCHES)

    def __isPM12Active(self):
        return self.__personalMissions.isCampaignActive(PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.REGULAR]) or self.__personalMissions.isCampaignActive(PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.PERSONAL_MISSION_2])

    def __isPM3Active(self):
        return self.__personalMissions.isCampaignActive(PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.PERSONAL_MISSION_3])
