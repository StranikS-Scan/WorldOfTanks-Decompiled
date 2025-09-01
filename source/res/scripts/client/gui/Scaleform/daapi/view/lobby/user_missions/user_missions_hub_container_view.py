# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/user_missions/user_missions_hub_container_view.py
from account_helpers.AccountSettings import MISSIONS_PAGE
from account_helpers import AccountSettings
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.user_missions import missions_group_packers
from gui.Scaleform.daapi.view.meta.UserMissionsHubContainerViewMeta import UserMissionsHubContainerViewMeta
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.USERMISSSIONS_ALIASES import USERMISSSIONS_ALIASES
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.tab_id import TabId
from gui.server_events.events_dispatcher import showMissionDetails, hideMissionDetails
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import UserMissionsEvent, MissionsEvent
from gui.shared.formatters import text_styles

class UserMissionsHubContainerView(UserMissionsHubContainerViewMeta):

    def __init__(self, ctx):
        self.__tabID = ctx.get('tab')
        self.__questId = ctx.get('questId')
        self.__commonTabView = None
        self.__eventID = ctx.get('eventID')
        self.__groupID = ctx.get('groupID')
        self.__showMissionDetails = ctx.get('showMissionDetails')
        self.__isFirstUpdate = True
        self.__builder = missions_group_packers.QuestsGroupsBuilder()
        self.__filterData = AccountSettings.getFilter(MISSIONS_PAGE)
        super(UserMissionsHubContainerView, self).__init__()
        return

    def registerFlashComponent(self, component, alias, *args):
        if alias == USERMISSSIONS_ALIASES.USER_MISSIONS_HUB_CONTENT_INJECT:
            super(UserMissionsHubContainerView, self).registerFlashComponent(component, alias, self.__tabID, self.__questId)
        else:
            super(UserMissionsHubContainerView, self).registerFlashComponent(component, alias)

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS:
            self.__commonTabView = viewPy
            self.__commonTabView.setBuilder(self.__builder, self.__filterData, self.__eventID)

    def resetFilters(self):
        self.__filterData = {'hideDone': False,
         'hideUnavailable': False}
        AccountSettings.setFilter(MISSIONS_PAGE, self.__filterData)
        if self.__commonTabView:
            self.__commonTabView.setFilters(self.__filterData)

    def onClose(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def _populate(self):
        super(UserMissionsHubContainerView, self)._populate()
        self.addListener(UserMissionsEvent.CHANGE_TAB, self.__onChangeTab, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(UserMissionsEvent.CHANGE_CONTENT_LAYOUT, self.__onChangeContentLayout, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(UserMissionsEvent.TRANSITION_TO_MISSION, self.__onTransitionToMission, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        super(UserMissionsHubContainerView, self)._dispose()
        self.removeListener(UserMissionsEvent.CHANGE_TAB, self.__onChangeTab, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(UserMissionsEvent.CHANGE_CONTENT_LAYOUT, self.__onChangeContentLayout, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(UserMissionsEvent.TRANSITION_TO_MISSION, self.__onTransitionToMission, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CHANGED, self.__onFilterChanged, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(MissionsEvent.ON_FILTER_CLOSED, self.__onFilterClosed, EVENT_BUS_SCOPE.LOBBY)
        self.__commonTabView = None
        return

    def __filterApplied(self):
        for attr in self.__filterData:
            if self.__filterData[attr]:
                return True

        return False

    def __updateFilterLabel(self):
        totalQuests = self.__commonTabView.getTotalQuestsCount()
        currentQuests = self.__commonTabView.getCurrentQuestsCount()
        style = text_styles.error if currentQuests == 0 else text_styles.stats
        countText = '{} / {}'.format(style(currentQuests), text_styles.standard(totalQuests))
        filterApplied = self.__filterApplied()
        self.as_showFilterCounterS(countText, filterApplied)
        if filterApplied:
            self.as_blinkFilterCounterS()

    def __onFilterChanged(self, event):
        if event.ctx != self.__filterData:
            self.__filterData = event.ctx
            if self.__commonTabView is not None:
                self.__commonTabView.setFilters(self.__filterData)
            self.__updateFilterLabel()
        return

    def __onFilterClosed(self, _):
        if self.__filterApplied():
            self.as_blinkFilterCounterS()

    def __onShowTab(self, resetFilters=False):
        isCommonTab = self.__tabID == TabId.COMMON
        self.as_updateCommonMissionsTabVisibilityS(isCommonTab)
        if isCommonTab:
            self.__updateFilterLabel()
            if resetFilters:
                self.resetFilters()
        background = R.images.gui.maps.icons.userMissions.hub.background.dyn(self.__tabID)
        self.as_setBackgroundS(backport.image(background()) if background.exists() else '')

    def __showMission(self):
        if self.__tabID == TabId.COMMON and self.__groupID is not None:
            self.__commonTabView.as_scrollToItemS('blockId', self.__groupID)
        if self.__eventID and self.__groupID and self.__showMissionDetails:
            showMissionDetails(self.__eventID, self.__groupID)
        else:
            hideMissionDetails()
        return

    def __onChangeTab(self, event):
        self.__tabID = event.tabID
        self.__onShowTab()
        if self.__isFirstUpdate:
            self.__showMission()
            self.__isFirstUpdate = False

    def __onChangeContentLayout(self, event):
        self.as_updateCommonMissionsTabPositionS(event.y, event.height)

    def __onTransitionToMission(self, event):
        self.__tabID = event.tabID
        self.__questId = event.questId
        self.__eventID = event.eventID
        self.__groupID = event.groupID
        self.__showMissionDetails = event.showMissionDetails
        self.__onShowTab(resetFilters=True)
        self.__showMission()
