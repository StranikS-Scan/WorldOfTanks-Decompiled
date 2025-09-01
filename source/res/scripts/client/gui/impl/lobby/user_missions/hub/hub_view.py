# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/hub_view.py
from collections import OrderedDict
from account_helpers.AccountSettings import Winback
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.hub_view_model import HubViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tab_model import TabModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.tab_id import TabId
from gui.impl.lobby.user_missions.hub.tabs.basic.basic_missions_tab import BasicMissionsTab
from gui.impl.lobby.user_missions.hub.update_children_mixin import UpdateChildrenMixin
from gui.impl.pub.view_component import ViewComponent
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showWinbackIntroView
from gui.shared.events import UserMissionsEvent
from gui.winback.winback_helpers import getWinbackSetting, setWinbackSetting
from helpers import dependency
from skeletons.gui.game_control import IWinbackController
TABS = OrderedDict([(TabId.BASIC, BasicMissionsTab)])

class HubView(ViewComponent[HubViewModel]):
    __winbackController = dependency.descriptor(IWinbackController)

    def __init__(self, tabID, questId):
        self.__tabID = tabID
        self.__questId = questId
        self.__isFirstLayoutUpdate = True
        self.__createdTabs = []
        super(HubView, self).__init__(R.views.mono.user_missions.hub(), HubViewModel)

    @property
    def viewModel(self):
        return super(HubView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(HubView, self)._onLoaded(*args, **kwargs)
        self._updateTabs()
        self.__update()

    def __update(self, *_):
        if self.__winbackController.isProgressionAvailable() and not self.__isWinbackIntroShown():
            self.__showWinbackIntroScreen()

    def __showWinbackIntroScreen(self):
        showWinbackIntroView()
        setWinbackSetting(Winback.INTRO_SHOWN, True)

    def __isWinbackIntroShown(self):
        return getWinbackSetting(Winback.INTRO_SHOWN)

    def _updateTabs(self):
        with self.viewModel.transaction() as vm:
            tabsList = vm.getTabsList()
            tabsList.clear()
            if umgConfigSchema.getModel().enableDailyWeeklyUI:
                tabsList.addViewModel(self.__createTab(TabId.BASIC, R.strings.user_missions.hub.basic_missions.title()))
            tabsList.addViewModel(self.__createTab(TabId.COMMON, R.strings.user_missions.hub.common_missions.title()))
            vm.setCurrentTabId(self.__tabID)
            tabsList.invalidate()
            tabIds = {tab.getId() for tab in tabsList}
            if self.__tabID in tabIds:
                self.__updateTab(self.__tabID)
            else:
                self.__changeTab(tabsList[0].getId())

    def _getEvents(self):
        return ((self.viewModel.onTabChange, self.__onTabChange), (self.viewModel.onContentLayoutChanged, self.__onContentLayoutChanged), (g_playerEvents.onConfigModelUpdated, self.__onConfigModelUpdated))

    def _getListeners(self):
        return ((UserMissionsEvent.TRANSITION_TO_MISSION, self.__onTransitionToMission, EVENT_BUS_SCOPE.LOBBY),)

    def __createTab(self, tabID, title):
        tab = TabModel()
        tab.setId(tabID)
        tab.setTitle(title)
        return tab

    def __updateTab(self, tabID):
        self.__tabID = tabID
        viewCls = TABS.get(self.__tabID)
        if self.__tabID in self.__createdTabs:
            if viewCls:
                tabView = self._getChild(viewCls.LAYOUT_ID)
                if isinstance(tabView, UpdateChildrenMixin):
                    tabView.update()
            return
        if viewCls:
            self._registerChild(viewCls.LAYOUT_ID, viewCls(self.__questId))
        self.__createdTabs.append(self.__tabID)

    def __changeTab(self, tabID):
        if tabID != self.viewModel.getCurrentTabId():
            self.__updateTab(tabID)
            self.viewModel.setCurrentTabId(self.__tabID)
            g_eventBus.handleEvent(UserMissionsEvent(UserMissionsEvent.CHANGE_TAB, self.__tabID), EVENT_BUS_SCOPE.LOBBY)

    def __onTabChange(self, args):
        self.__changeTab(args.get('tabId'))

    def __onContentLayoutChanged(self, args):
        g_eventBus.handleEvent(UserMissionsEvent(UserMissionsEvent.CHANGE_CONTENT_LAYOUT, y=args.get('y'), height=args.get('height')), EVENT_BUS_SCOPE.LOBBY)
        if self.__isFirstLayoutUpdate:
            self.__isFirstLayoutUpdate = False
            g_eventBus.handleEvent(UserMissionsEvent(UserMissionsEvent.CHANGE_TAB, self.__tabID), EVENT_BUS_SCOPE.LOBBY)

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            self._updateTabs()

    def __onTransitionToMission(self, event):
        self.__changeTab(event.tabID)
