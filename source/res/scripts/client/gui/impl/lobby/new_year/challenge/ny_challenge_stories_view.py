# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_stories_view.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_stories_view_model import ChallengeStoriesViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.events import NyGladeVisibilityEvent, NyCelebrityStoriesEvent, LobbySimpleEvent
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency, uniprof
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_constants import GuestsQuestsTokens, parseCelebrityTokenActionType, GuestQuestTokenActionType
from skeletons.gui.app_loader import IAppLoader
from skeletons.new_year import ICelebrityController, INewYearController
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from new_year.ny_constants import NYObjects
_CHANGE_LAYERS_VISIBILITY = (WindowLayer.VIEW, WindowLayer.WINDOW)

class ChallengeStoriesView(ViewImpl):
    __slots__ = ('__selectedLevel', '__justReceived', '__blur')
    __celebrityController = dependency.descriptor(ICelebrityController)
    __nyController = dependency.descriptor(INewYearController)
    __appLoader = dependency.instance(IAppLoader)

    def __init__(self, level, justReceived):
        settings = ViewSettings(R.views.lobby.new_year.ChallengeStoriesView())
        settings.model = ChallengeStoriesViewModel()
        self.__selectedLevel = level
        self.__justReceived = justReceived
        self.__blur = None
        super(ChallengeStoriesView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ChallengeStoriesView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChallengeStoriesView, self)._onLoading(*args, **kwargs)
        selectedIndex = 0
        with self.viewModel.transaction() as tx:
            stories = tx.getStories()
            stories.clear()
            storiesQuests = GuestsQuestsConfigHelper.getStoryGuestQuests(GuestsQuestsTokens.GUEST_A)
            completedQuests = [ q.getQuestID() for q in storiesQuests if self.__celebrityController.isGuestQuestCompleted(q) ]
            for index, quest in enumerate(storiesQuests):
                questID = quest.getQuestID()
                tokenID = GuestsQuestsConfigHelper.getQuestActionToken(quest, GuestQuestTokenActionType.STORY)
                if tokenID:
                    _, _, level = parseCelebrityTokenActionType(tokenID)
                    if self.__selectedLevel == level:
                        selectedIndex = index
                storyID = questID if questID in completedQuests else ''
                stories.addString(storyID)

            tx.setSelectIndex(selectedIndex)
            tx.setAmountOfCompletedStories(len(completedQuests))
            stories.invalidate()

    def _onLoaded(self, *args, **kwargs):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': False}), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_IN), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(NyCelebrityStoriesEvent(eventType=NyCelebrityStoriesEvent.STORIES_VIEW_OPENED), scope=EVENT_BUS_SCOPE.DEFAULT)
        if not NewYearNavigation.getCurrentObject():
            self.destroyWindow()

    @uniprof.regionDecorator(label='ny_challenge_stories', scope='enter')
    def _initialize(self, *args, **kwargs):
        self.__blur = CachedBlur(blurRadius=0.3, enabled=True)
        self.__changeLayersVisibility(True, _CHANGE_LAYERS_VISIBILITY)
        self.__nyController.onStateChanged += self.__onEventStateChanged
        NewYearNavigation.onObjectStateChanged += self.__onNavigation

    @uniprof.regionDecorator(label='ny_challenge_stories', scope='exit')
    def _finalize(self):
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_OUT), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(NyCelebrityStoriesEvent(eventType=NyCelebrityStoriesEvent.STORIES_VIEW_CLOSED, ctx={'justReceived': self.__justReceived}), scope=EVENT_BUS_SCOPE.DEFAULT)
        self.__changeLayersVisibility(False, _CHANGE_LAYERS_VISIBILITY)
        self.__nyController.onStateChanged -= self.__onEventStateChanged
        NewYearNavigation.onObjectStateChanged -= self.__onNavigation
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(ChallengeStoriesView, self)._finalize()
        return

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()
            NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, objectName=NYObjects.CHALLENGE, forceShowMainView=True)

    def __onNavigation(self):
        self.destroyWindow()

    def __changeLayersVisibility(self, isHide, layers):
        lobby = self.__appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(layers, time=0.3)
            else:
                lobby.containerManager.showContainers(layers, time=0.3)
            self.__appLoader.getApp().graphicsOptimizationManager.switchOptimizationEnabled(not isHide)


class ChallengeStoriesViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, level=None, justReceived=None, parent=None):
        super(ChallengeStoriesViewWindow, self).__init__(content=ChallengeStoriesView(level, justReceived), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
