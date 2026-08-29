# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/basic_missions_tab.py
from __future__ import absolute_import
import typing
from future.utils import listvalues
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getSuitableVehicles
from helpers import dependency
from gui.impl.gen import R
from personal_missions import PM_BRANCH, PM_SWITCHES
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
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, List

class BasicMissionsTab(UpdateChildrenMixin, ViewComponent[BasicMissionsTabModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.MainView()
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, targetQuestId):
        self._targetQuestId = targetQuestId
        self._hasSuitableVehicles = False
        self.__personalMissions = self.eventsCache.getPersonalMissions()
        self.__pmOperations = self.__personalMissions.getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES)
        self.__activeCampaigns = set(self.__personalMissions.getActiveCampaigns())
        super(BasicMissionsTab, self).__init__(model=BasicMissionsTabModel)

    @property
    def viewModel(self):
        return super(BasicMissionsTab, self).getViewModel()

    def _finalize(self):
        self.__personalMissions = None
        self.__pmOperations = {}
        self.__activeCampaigns = {}
        super(BasicMissionsTab, self)._finalize()
        return

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
        pm3SwitcherIndex = len(PM_BRANCH.WITH_AWARD_LIST_BRANCHES)
        campaignSwitchers = PM_SWITCHES.ALL[pm3SwitcherIndex:]
        allSwitchers = campaignSwitchers + (PM_SWITCHES.DISABLED_PM_OPERATIONS,)
        if any((switcher in diff for switcher in allSwitchers)):
            if not all((diff.get(switcher, True) for switcher in campaignSwitchers)) or list(self.__pmOperations) & diff.get(PM_SWITCHES.DISABLED_PM_OPERATIONS, {}).keys():
                self.viewModel.setIsPMSectionAvailable(False)
            else:
                self.__updatePersonalMissionSection()

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            self._updateDailyBlockStatus()

    def __updatePersonalMissionSection(self):
        self.viewModel.setIsPMSectionAvailable(self.__isCampaignEnabled() and not self.__isPMOperationDisabled() and not self.__isCampaignCompleted() and (self.__isCampaignActive(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES) or (self._hasSuitableVehicles or self.__isCampaignActive(PM_BRANCH.WITH_AWARD_LIST_BRANCHES)) and not self.__isCampaignStarted()))

    def __onCacheSyncCompleted(self, *_):
        self.__updatePersonalMissionSection()

    def __onInventoryCacheSyncCompleted(self, reason, _):
        if reason == CACHE_SYNC_REASON.INVENTORY_RESYNC:
            self.__updatePersonalMissionSection()

    def __onVehiclesInventorySyncCompleted(self, _):
        self._hasSuitableVehicles = bool(getSuitableVehicles())
        self.__updatePersonalMissionSection()

    def __isCampaignCompleted(self):
        return all((operation.isFullCompleted() for operation in listvalues(self.__pmOperations)))

    def __isCampaignEnabled(self):
        settings = self.lobbyContext.getServerSettings()
        return any((settings.isPersonalMissionsEnabled(campaign) for campaign in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES))

    def __isCampaignStarted(self):
        return self.__personalMissions.isWithoutAwardListBranchActivated()

    def __isCampaignActive(self, branchNames):
        return bool(self.__activeCampaigns.intersection(branchNames))

    def __isPMOperationDisabled(self):
        return any((operation.isDisabled() for operation in listvalues(self.__pmOperations)))
