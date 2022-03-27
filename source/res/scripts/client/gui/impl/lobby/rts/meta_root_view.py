# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/meta_root_view.py
import logging
from collections import namedtuple
from gui.shared.utils import getPlayerDatabaseID
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.impl.backport.backport_context_menu import createContextMenuData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.meta_root_view_model import MetaRootViewModel
from gui.impl.gen.view_models.views.lobby.rts.meta_tab_model import Tabs, MetaTabModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.rts.collection_view import RTSCollectionView
from gui.impl.lobby.rts.quests_view import QuestsView
from gui.impl.lobby.rts.statistics_view import StatisticsView
from gui.impl.lobby.rts.leaderboard_view import LeaderboardView
from gui.impl.pub import ViewImpl
from gui.impl.backport.backport_context_menu import BackportContextMenuWindow
from gui.Scaleform.Waiting import Waiting
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController, IRTSProgressionController
_logger = logging.getLogger(__name__)
_SubviewDescriptor = namedtuple('SubviewDescriptor', ('name', 'resId', 'viewClass', 'hasNotification'))
_TABS = (_SubviewDescriptor(name=Tabs.COLLECTION, resId=R.views.lobby.rts.CollectionView(), viewClass=RTSCollectionView, hasNotification=True),
 _SubviewDescriptor(name=Tabs.QUESTS, resId=R.views.lobby.rts.QuestsView(), viewClass=QuestsView, hasNotification=False),
 _SubviewDescriptor(name=Tabs.STATISTICS, resId=R.views.lobby.rts.StatisticsView(), viewClass=StatisticsView, hasNotification=False),
 _SubviewDescriptor(name=Tabs.LEADERBOARD, resId=R.views.lobby.rts.LeaderboardView(), viewClass=LeaderboardView, hasNotification=False))

def getMemberContextMenuData(event):
    userName = event.getArgument('username')
    spaId = int(event.getArgument('spaId'))
    if spaId == getPlayerDatabaseID():
        return None
    else:
        context = {'dbID': spaId,
         'userName': userName,
         'customItems': [],
         'excludedItems': [],
         'customItemsAfterEnd': []}
        _logger.debug('getMemberContextMenuData: %s', context)
        return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.CUSTOM_USER, context)


class MetaRootView(ViewImpl):
    __slots__ = ()
    __rtsBattlesController = dependency.descriptor(IRTSBattlesController)
    __progressionCtrl = dependency.descriptor(IRTSProgressionController)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = MetaRootViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MetaRootView, self).__init__(settings)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getMemberContextMenuData(event)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(MetaRootView, self).createContextMenu(event)

    def changeTab(self, tabId):
        if tabId not in (t.value for t in Tabs):
            _logger.error('Wrong tabId: %s', tabId)
            return
        currTabId = self.viewModel.getTabId()
        if tabId == currTabId:
            return
        if currTabId:
            currtabData = next((tab for tab in _TABS if tab.name.value == currTabId))
            currTab = self.getChildView(currtabData.resId)
            currTab.hideTab()
        tabData = next((tab for tab in _TABS if tab.name.value == tabId))
        nextTab = self.getChildView(tabData.resId)
        if tabData.hasNotification:
            nextTab.markSeen()
            self.__updateTabs()
        nextTab.showTab()
        self.viewModel.setTabId(tabId)

    @property
    def viewModel(self):
        return super(MetaRootView, self).getViewModel()

    def _onLoading(self, tabId=None):
        if not Waiting.isOpened('loadPage'):
            Waiting.show('loadPage')
        if tabId is None:
            tabId = Tabs.COLLECTION.value
        self.__initTabs()
        self.changeTab(tabId)
        self.__addListeners()
        return

    def _onLoaded(self, *args, **kwargs):
        super(MetaRootView, self)._onLoaded(*args, **kwargs)
        self.__toggleHeaderMenu(False)
        Waiting.hide('loadPage')

    def _finalize(self):
        self.__removeListeners()
        self.__toggleHeaderMenu(True)

    def __initTabs(self):
        for tab in _TABS:
            view = tab.viewClass(tab.resId)
            self.setChildView(tab.resId, view)

        with self.viewModel.transaction() as tx:
            tabs = tx.getTabs()
            tabs.clear()
            for tab in _TABS:
                tabModel = MetaTabModel()
                tabModel.setName(tab.name)
                tabModel.setResId(tab.resId)
                if tab.hasNotification:
                    view = self.getChildView(tab.resId)
                    tabModel.setShowNotificationBubble(view.hasNewContent())
                tabs.addViewModel(tabModel)

            tabs.invalidate()

    def __updateTabs(self):
        with self.viewModel.transaction() as tx:
            tabs = tx.getTabs()
            for index, tab in enumerate(_TABS):
                if tab.hasNotification:
                    view = self.getChildView(tab.resId)
                    tabs[index].setShowNotificationBubble(view.hasNewContent())

            tabs.invalidate()

    def __addListeners(self):
        self.viewModel.onTabClick += self.__onTabClick
        self.viewModel.onAbout += self.__onAbout
        self.viewModel.onClose += self.__onClose
        self.__progressionCtrl.onProgressUpdated += self.__updateTabs

    def __removeListeners(self):
        self.viewModel.onTabClick -= self.__onTabClick
        self.viewModel.onAbout -= self.__onAbout
        self.viewModel.onClose -= self.__onClose
        self.__progressionCtrl.onProgressUpdated -= self.__updateTabs

    @args2params(str)
    def __onTabClick(self, tabId):
        self.changeTab(tabId)

    @staticmethod
    def __onClose():
        showHangar()

    def __onAbout(self):
        self.__rtsBattlesController.showRTSInfoPage(VIEW_ALIAS.BROWSER_OVERLAY)

    @staticmethod
    def __toggleHeaderMenu(isVisible):
        state = HeaderMenuVisibilityState.ALL if isVisible else HeaderMenuVisibilityState.NOTHING
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), EVENT_BUS_SCOPE.LOBBY)
