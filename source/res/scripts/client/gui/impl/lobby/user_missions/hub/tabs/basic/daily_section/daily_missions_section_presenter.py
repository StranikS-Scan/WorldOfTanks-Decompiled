# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/daily_section/daily_missions_section_presenter.py
from constants import PremiumConfigs, DAILY_QUESTS_CONFIG
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.daily_missions_section_model import DailyMissionsSectionModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.reward_progress_block_model import RewardProgressTypes
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.tab_id import TabId
from gui.impl.lobby.missions.missions_helpers import isPremiumPlusAccount
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.presenters.daily_missions_block_presenter import DailyMissionsBlockPresenter
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.presenters.premium_daily_missions_block_presenter import PremiumDailyMissionsBlockPresenter
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.presenters.reward_progress_block_presenter import RewardProgressBlockPresenter
from gui.impl.lobby.user_missions.hub.update_children_mixin import UpdateChildrenMixin
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.events_helpers import isDailyQuestsEnable, isPremiumQuestsEnable
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import UserMissionsEvent
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
TAB_ID = TabId.BASIC

class DailyMissionsSectionPresenter(UpdateChildrenMixin, ViewComponent[DailyMissionsSectionModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.DailyMissionsSection.MainView()
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, targetQuestId=''):
        if targetQuestId is None:
            targetQuestId = ''
        super(DailyMissionsSectionPresenter, self).__init__(model=DailyMissionsSectionModel)
        self._premiumDailyMissionsChild = None
        self._targetQuestId = targetQuestId
        return

    @property
    def viewModel(self):
        return super(DailyMissionsSectionPresenter, self).getViewModel()

    def _getListeners(self):
        return ((UserMissionsEvent.CHANGE_TAB, self.__onTabChange, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),)

    def _getChildComponents(self):
        userMissions = R.aliases.user_missions.hub.basicMissions.DailyMissionsSection
        return {userMissions.DailyBlock(): DailyMissionsBlockPresenter,
         userMissions.PremiumBlock(): PremiumDailyMissionsBlockPresenter,
         userMissions.RewardProgressBlock(): self.__addRewardProgressChild}

    def _onLoading(self, *args, **kwargs):
        super(DailyMissionsSectionPresenter, self)._onLoading()
        self.__updateModel()

    def __addRewardProgressChild(self):
        self._rewardProgressChild = RewardProgressBlockPresenter()
        return self._rewardProgressChild

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            isDailyEnabled = isDailyQuestsEnable()
            tx.dailyMissionsBlockStatus.setIsEnabled(isDailyEnabled)
            tx.setTargetQuestId(self._targetQuestId)
            if not isDailyEnabled:
                tx.dailyMissionsBlockStatus.setDisabilityReason(backport.text(R.strings.user_missions.hub.basic_missions.daily.regular.not_available.generic()))
            isPremiumEnabled = isPremiumQuestsEnable()
            tx.premiumDailyMissionsBlockStatus.setIsEnabled(isPremiumEnabled)
            isPremAcc = isPremiumPlusAccount()
            if not isPremAcc or not isPremiumEnabled:
                tx.premiumDailyMissionsBlockStatus.setDisabilityReason(backport.text(R.strings.user_missions.hub.basic_missions.daily.premium.not_available.generic()))
            progressType = self._rewardProgressChild.progressType
            tx.rewardProgressBlockStatus.setIsEnabled(progressType != RewardProgressTypes.DISABLED)
            tx.rewardProgressBlockStatus.setDisabilityReason(backport.text(R.strings.user_missions.hub.reward_progress.epic_quest_progress.disabled()))

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff or PremiumConfigs.PREM_QUESTS in diff:
            self.__updateModel()

    def __onTabChange(self, ume):
        if self._targetQuestId and ume.tabID != TabId.BASIC:
            with self.viewModel.transaction() as tx:
                self._targetQuestId = ''
                tx.setTargetQuestId(self._targetQuestId)
