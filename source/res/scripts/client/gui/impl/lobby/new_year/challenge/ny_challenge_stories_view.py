# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_stories_view.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_stories_view_model import ChallengeStoriesViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.events import NyGladeVisibilityEvent, NyCelebrityStoriesEvent, LobbySimpleEvent
from helpers import dependency, uniprof
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_constants import GuestsQuestsTokens, parseCelebrityTokenActionType, GuestQuestTokenActionType
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.gui.app_loader import IAppLoader
from skeletons.new_year import ICelebrityController, INewYearController
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from new_year.ny_constants import AdditionalCameraObject
_CHANGE_LAYERS_VISIBILITY = (WindowLayer.VIEW, WindowLayer.WINDOW)

class ChallengeStoriesView(ViewImpl):
    __slots__ = ('__storyBy', '__selectedLevel')
    __celebrityController = dependency.descriptor(ICelebrityController)
    __nyController = dependency.descriptor(INewYearController)
    __appLoader = dependency.instance(IAppLoader)

    def __init__(self, storyBy, level):
        settings = ViewSettings(R.views.lobby.new_year.ChallengeStoriesView())
        settings.model = ChallengeStoriesViewModel()
        self.__storyBy = storyBy or GuestsQuestsTokens.GUEST_A
        self.__selectedLevel = level
        super(ChallengeStoriesView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChallengeStoriesView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ChallengeStoriesView, self)._onLoading(*args, **kwargs)
        selectedIndex = 0
        with self.viewModel.transaction() as tx:
            stories = tx.getStories()
            stories.clear()
            storiesQuests = GuestsQuestsConfigHelper.getStoryGuestQuests(self.__storyBy)
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
            tx.setStoryBy(self.__storyBy)
            tx.setIsMaxAtmosphereLevel(NewYearAtmospherePresenter.isMaxLevel())
            stories.invalidate()

    def _onLoaded(self, *args, **kwargs):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': False}), scope=EVENT_BUS_SCOPE.LOBBY)

    @uniprof.regionDecorator(label='ny_challenge_stories', scope='enter')
    def _initialize(self, *args, **kwargs):
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_IN), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(NyCelebrityStoriesEvent(eventType=NyCelebrityStoriesEvent.STORIES_VIEW_OPENED), scope=EVENT_BUS_SCOPE.DEFAULT)
        self.__changeLayersVisibility(True, _CHANGE_LAYERS_VISIBILITY)
        self.__nyController.onStateChanged += self.__onEventStateChanged

    @uniprof.regionDecorator(label='ny_challenge_stories', scope='exit')
    def _finalize(self):
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_OUT), scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        ctx = {}
        ctx['guestName'] = self.__storyBy
        g_eventBus.handleEvent(NyCelebrityStoriesEvent(eventType=NyCelebrityStoriesEvent.STORIES_VIEW_CLOSED, ctx=ctx), scope=EVENT_BUS_SCOPE.DEFAULT)
        self.__changeLayersVisibility(False, _CHANGE_LAYERS_VISIBILITY)
        self.__nyController.onStateChanged -= self.__onEventStateChanged
        super(ChallengeStoriesView, self)._finalize()

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()
            NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, objectName=AdditionalCameraObject.CHALLENGE, forceShowMainView=True)

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

    def __init__(self, storyBy=None, level=None, parent=None):
        super(ChallengeStoriesViewWindow, self).__init__(content=ChallengeStoriesView(storyBy, level), parent=parent, layer=WindowLayer.TOP_WINDOW)
