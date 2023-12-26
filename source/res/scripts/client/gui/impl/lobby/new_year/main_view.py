# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/main_view.py
import weakref
from functools import partial
import typing
import BigWorld
from HeroTank import HeroTank
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_glade_view_model import AnimationLevelUpStates
from gui.impl.gen.view_models.views.lobby.new_year.views.main_view_model import MainViewModel, MainViews, SwitchStates
from gui.impl.lobby.new_year.ny_menu_component import NYMainMenu
from gui.impl.lobby.new_year.ny_sidebar_component import NYSidebar
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.ny_views_helpers import executeContext
from gui.impl.new_year.navigation import NewYearNavigation, VIEW_ALIAS_TO_MENU_NAME, ViewAliases
from gui.impl.new_year.sounds import NY_MAIN_VIEW_SOUND_SPACE, NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showHeroTankPreview
from helpers import dependency, uniprof
from new_year.ny_constants import NyWidgetTopMenu, NYObjects
from shared_utils import nextTick
from gui.shared.events import NyGladeVisibilityEvent, LobbySimpleEvent
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, IFriendServiceController
from uilogging.ny.loggers import NyMainViewFlowLogger, NyMainViewLogger
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.shared.event_dispatcher import NYViewCtx
_SubModelInfo = typing.NamedTuple('_SubModelInfo', [('ID', MainViews), ('presenter', NyHistoryPresenter), ('canBeLoaded', typing.Optional[typing.Callable[[], bool]])])
_STAGE_ENABLED_TAB = (NyWidgetTopMenu.GLADE,
 NyWidgetTopMenu.CHALLENGE,
 NyWidgetTopMenu.FRIEND_GLADE,
 NyWidgetTopMenu.FRIEND_CHALLENGE,
 NyWidgetTopMenu.MARKETPLACE,
 NyWidgetTopMenu.GIFT_MACHINE)
_DEFAULT_PREV_VIEW_ALIAS_FOR_INFO = {MainViews.INFO: ViewAliases.GLADE_VIEW,
 MainViews.FRIEND_INFO: ViewAliases.FRIEND_GLADE_VIEW}

class MainView(ViewImpl):
    __slots__ = ('__ctx', '__backCallback', '__contentPresentersMap', '__componentPresenters', '__preCtx', '__regionName')
    _COMMON_SOUND_SPACE = NY_MAIN_VIEW_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __friendsService = dependency.descriptor(IFriendServiceController)
    __appLoader = dependency.descriptor(IAppLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __flowLogger = NyMainViewFlowLogger()
    __uiLogger = NyMainViewLogger()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.MainView())
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = MainViewModel()
        self.__ctx = kwargs.get('ctx', None)
        self.__preCtx = None
        self.__backCallback = None
        self.__contentPresentersMap = {}
        self.__componentPresenters = []
        self.__appLoader.getApp().setBackgroundAlpha(0.0)
        self.__regionName = None
        super(MainView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentPresenter(self):
        return self.__contentPresentersMap[self.__ctx.menuName].presenter

    def createToolTipContent(self, event, contentID):
        for presenter in self.__componentPresenters:
            content = presenter.createToolTipContent(event, contentID)
            if content is not None:
                return content

        return self.currentPresenter.createToolTipContent(event, contentID)

    def createToolTip(self, event):
        return self.currentPresenter.createToolTip(event) or super(MainView, self).createToolTip(event)

    def createPopOverContent(self, event):
        for presenter in self.__componentPresenters:
            content = presenter.createPopOverContent(event)
            if content is not None:
                return content

        return self.currentPresenter.createPopOverContent(event) or super(MainView, self).createPopOverContent(event)

    def _initialize(self, *args, **kwargs):
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': False}), EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.gladeModel.setAnimationLevelUpState(AnimationLevelUpStates.IDLE)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOM)
        NewYearNavigation.closeMainViewInProcess(False)

    def _getEvents(self):
        return super(MainView, self)._getEvents() + ((self.viewModel.onClose, self.__onCloseClick),
         (self.viewModel.onStartClose, self.__onStartClose),
         (self.viewModel.onFadeInDone, self.__onFadeInDone),
         (self.viewModel.backButton.onBack, self.__onBackClicked),
         (self.viewModel.onGlobalFadeIn, self.__onGlobalFadeIn),
         (self.viewModel.onGlobalFadeOut, self.__onGlobalFadeOut),
         (self.__nyController.onStateChanged, self.__onStateChanged),
         (self.__friendsService.onFriendServiceStateChanged, self.__onChangeFriendService),
         (self.__settingsCore.onSettingsChanged, self.__onSettingsChanged),
         (NewYearNavigation.onPreSwitchView, self.__onPreSwitchViewEvent),
         (NewYearNavigation.updateBackButton, self.__onBackButtonUpdated))

    def _getListeners(self):
        return super(MainView, self)._getListeners() + ((CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated, EVENT_BUS_SCOPE.DEFAULT),
         (NyGladeVisibilityEvent.START_FADE_IN, self.__handleStartFadeIn, EVENT_BUS_SCOPE.DEFAULT),
         (NyGladeVisibilityEvent.START_FADE_OUT, self.__handleStartFadeOut, EVENT_BUS_SCOPE.DEFAULT),
         (LobbySimpleEvent.WAITING_SHOWN, self.__showWaiting, EVENT_BUS_SCOPE.LOBBY),
         (LobbySimpleEvent.WAITING_HIDDEN, self.__hideWaiting, EVENT_BUS_SCOPE.LOBBY))

    def _onLoading(self, *args, **kwargs):
        super(MainView, self)._onLoading(args, kwargs)
        self.__registerSubModels()
        for presenter in self.__componentPresenters:
            presenter.initialize()

        tutorialState = self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE)
        if tutorialState:
            self.viewModel.setTutorialState(tutorialState)
        else:
            self.viewModel.setTutorialState(TutorialStates.INTRO)
        self.viewModel.setIsAnimatedShow(self.__ctx and not self.__ctx.kwargs.get('forceShowMainView', False))
        self.__switchSubView(self.__ctx)

    def _onLoaded(self, *args, **kwargs):
        self.__uiLogger.start()
        nextTick(partial(self.__hangarSpace.setVehicleSelectable, True))()
        nextTick(partial(self.__onStateChanged))()
        params = self.__ctx.kwargs
        executeAfterLoaded = params.get('executeAfterLoaded')
        if executeAfterLoaded:
            executeContext(executeAfterLoaded)

    def _finalize(self):
        if dependency.instance(IHangarSpace).spaceInited:
            BigWorld.worldDrawEnabled(True)
        if self.__friendsService.isInFriendHangar:
            self.__friendsService.leaveFriendHangar()
        self.__uiLogger.stop()
        self.__flowLogger.logFinalize(self.__ctx.menuName, self.currentPresenter.currentTab)
        self.__hangarSpace.setVehicleSelectable(False)
        for presenter in self.__componentPresenters:
            presenter.finalize()
            presenter.clear()

        self.__componentPresenters = None
        self.currentPresenter.finalize()
        self.currentPresenter.clearTabCache()
        self.currentPresenter.clearHistory()
        if self.__regionName:
            uniprof.exitFromRegion(self.__regionName)
            self.__regionName = None
        for subModelInfo in self.__contentPresentersMap.itervalues():
            subModelInfo.presenter.clear()

        self.__contentPresentersMap.clear()
        self.__contentPresentersMap = None
        NewYearNavigation.clear()
        self.__backCallback = None
        self.__ctx = None
        self.__preCtx = None
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': True}), EVENT_BUS_SCOPE.LOBBY)
        super(MainView, self)._finalize()
        return

    def __updateWaitingStatus(self, isWaitingShown):
        if self.viewModel is None:
            return
        else:
            self.viewModel.setIsWaitingShown(isWaitingShown)
            return

    def __showWaiting(self, _):
        self.__updateWaitingStatus(True)

    def __hideWaiting(self, _):
        self.__updateWaitingStatus(False)

    def __registerSubModels(self):
        self.__contentPresentersMap = _PresentersMap(self)
        self.__componentPresenters.extend([NYMainMenu(self.viewModel.mainMenu, self), NYSidebar(self.viewModel.sidebar, self)])

    def __onPreSwitchViewEvent(self, ctx):
        if ctx.kwargs.get('isObjectSwitched', False):
            self.viewModel.setSwitchState(SwitchStates.WITH_SWITCHING_OBJS)
        else:
            self.viewModel.setSwitchState(SwitchStates.DEFAULT)
        subModelInfo = self.__contentPresentersMap[ctx.menuName]
        subModelInfo.presenter.preLoad(*ctx.args, **ctx.kwargs)
        self.__preCtx = ctx

    def __onFadeInDone(self):
        if self.__preCtx is not None:
            self.__switchSubView(self.__preCtx)
            self.viewModel.setSwitchState(SwitchStates.DONE)
            self.__preCtx = None
        return

    def __switchSubView(self, ctx):
        if self.__regionName:
            uniprof.exitFromRegion(self.__regionName)
        self.__regionName = ctx.menuName
        uniprof.enterToRegion(self.__regionName)
        if dependency.instance(IHangarSpace).spaceInited:
            BigWorld.worldDrawEnabled(ctx.menuName in _STAGE_ENABLED_TAB)
        subModelInfo = self.__contentPresentersMap[ctx.menuName]
        if subModelInfo.canBeLoaded is not None and not subModelInfo.canBeLoaded():
            return
        else:
            if subModelInfo.ID in _DEFAULT_PREV_VIEW_ALIAS_FOR_INFO:
                prevViewAlias = ctx.kwargs.get('previousViewAlias', _DEFAULT_PREV_VIEW_ALIAS_FOR_INFO.get(subModelInfo.ID))
                prevSubModelInfo = self.__contentPresentersMap[VIEW_ALIAS_TO_MENU_NAME[prevViewAlias]]
                self.currentPresenter.clearHistory()
                prevSubModelInfo.presenter.addToHistoryForced()
            if self.currentPresenter.isLoaded:
                self.currentPresenter.finalize()
            with self.viewModel.transaction() as tx:
                subModelInfo.presenter.initialize(tabName=ctx.tabName, *ctx.args, **ctx.kwargs)
                tx.setViewType(subModelInfo.ID)
            self.__ctx = ctx
            NewYearNavigation.onSwitchView(ctx)
            return

    def __onStateChanged(self):
        if not self.__nyController.isEnabled():
            self.__onClose()

    def __onChangeFriendService(self):
        if self.__friendsService.isServiceEnabled is False and self.__friendsService.isInFriendHangar:
            self.__friendsService.leaveFriendHangar()
            NewYearNavigation.switchToView(ViewAliases.GLADE_VIEW, tabName=NYObjects.TOWN)

    def __onClose(self):
        NewYearNavigation.closeMainView()

    def __onCloseClick(self, args):
        isEscPressed = args.get('isEscPressed', False)
        self.__uiLogger.logExit(isEscPressed)
        self.__flowLogger.logCloseClick(self.__ctx.menuName, self.currentPresenter.currentTab, isEscPressed)
        self.__onClose()

    def __onStartClose(self):
        NewYearNavigation.closeMainViewInProcess(True)

    def __onBackButtonUpdated(self, ctx):
        self.__backCallback = ctx.get('callback')
        if self.viewModel is None:
            return
        elif not ctx.get('isVisible') and self.viewModel.backButton.getIsVisible() or self.__backCallback is None:
            self.__clearBackButton()
            return
        else:
            with self.viewModel.transaction() as model:
                model.backButton.setIsVisible(True)
                model.backButton.setCaption(ctx.get('caption', backport.text(R.strings.ny.backButton.label())))
                model.backButton.setGoTo(ctx.get('goTo', ''))
            return

    def __handleStartFadeIn(self, *_):
        with self.viewModel.transaction() as model:
            model.setIsGlobalFaded(True)

    def __handleStartFadeOut(self, _):
        with self.viewModel.transaction() as model:
            model.setIsGlobalFaded(False)

    def __onGlobalFadeIn(self):
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.END_FADE_IN), scope=EVENT_BUS_SCOPE.DEFAULT)

    def __onGlobalFadeOut(self):
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.END_FADE_OUT), scope=EVENT_BUS_SCOPE.DEFAULT)

    def __onBackClicked(self):
        if self.__backCallback is not None:
            self.__backCallback()
        return

    def __clearBackButton(self):
        self.__backCallback = None
        with self.viewModel.transaction() as model:
            model.backButton.setIsVisible(False)
            model.backButton.setCaption('')
            model.backButton.setGoTo('')
        return

    def __handleSelectedEntityUpdated(self, event):
        ctx = event.ctx
        if ctx['state'] != CameraMovementStates.FROM_OBJECT:
            entity = BigWorld.entities.get(ctx['entityId'], None)
            if isinstance(entity, HeroTank):
                descriptor = entity.typeDescriptor
                if descriptor:
                    showHeroTankPreview(descriptor.type.compactDescr)
        return

    def __onSettingsChanged(self, diff):
        if NewYearStorageKeys.TUTORIAL_STATE in diff:
            self.viewModel.setTutorialState(diff[NewYearStorageKeys.TUTORIAL_STATE])


class _PresentersMap(object):

    def __init__(self, mainView):
        self.__presentersCache = {}
        self.__mainView = weakref.proxy(mainView)
        self.__loadersMap = self.__makeLoadersMap()

    def itervalues(self):
        return self.__presentersCache.itervalues()

    def clear(self):
        self.__loadersMap = {}
        self.__presentersCache = {}
        self.__mainView = None
        return

    def __getitem__(self, item):
        if item not in self.__presentersCache:
            self.__tryToLoadPresenter(item)
        return self.__presentersCache.get(item, None)

    def __tryToLoadPresenter(self, key):
        if key in self.__loadersMap:
            self.__presentersCache[key] = self.__loadersMap[key]()

    def __makeLoadersMap(self):
        return {NyWidgetTopMenu.GLADE: partial(self.__makeSubModel, MainViews.GLADE, self.__loadGlade),
         NyWidgetTopMenu.GIFT_MACHINE: partial(self.__makeSubModel, MainViews.GIFT_MACHINE, self.__loadGiftMachine),
         NyWidgetTopMenu.INFO: partial(self.__makeSubModel, MainViews.INFO, self.__loadInfo),
         NyWidgetTopMenu.REWARDS: partial(self.__makeSubModel, MainViews.REWARDS, self.__loadRewards),
         NyWidgetTopMenu.MARKETPLACE: partial(self.__makeSubModel, MainViews.MARKETPLACE, self.__loadMarketplace),
         NyWidgetTopMenu.CHALLENGE: partial(self.__makeSubModel, MainViews.CHALLENGE, self.__loadChallenge),
         NyWidgetTopMenu.FRIENDS: partial(self.__makeSubModel, MainViews.FRIENDS, self.__loadFriends),
         NyWidgetTopMenu.FRIEND_INFO: partial(self.__makeSubModel, MainViews.FRIEND_INFO, self.__loadInfo),
         NyWidgetTopMenu.FRIEND_GLADE: partial(self.__makeSubModel, MainViews.FRIEND_GLADE, self.__loadFriendGlade),
         NyWidgetTopMenu.FRIEND_CHALLENGE: partial(self.__makeSubModel, MainViews.FRIEND_CHALLENGE, self.__loadFriendChallenge)}

    def __loadGlade(self):
        from gui.impl.lobby.new_year.glade.ny_glade_view import NyGladeView
        return NyGladeView(self.__mainView.viewModel.gladeModel, self.__mainView)

    def __loadGiftMachine(self):
        from gui.impl.lobby.new_year.gift_machine.ny_gift_machine_view import NyGiftMachineView
        return NyGiftMachineView(self.__mainView.viewModel.giftMachineModel, self.__mainView)

    def __loadInfo(self):
        from gui.impl.lobby.new_year.info_page.ny_info_view import NyInfoView
        return NyInfoView(self.__mainView.viewModel.infoModel, self.__mainView)

    def __loadRewards(self):
        from gui.impl.lobby.new_year.rewards_info.ny_rewards_info_view import NyRewardsInfoView
        return NyRewardsInfoView(self.__mainView.viewModel.rewardsModel, self.__mainView)

    def __loadMarketplace(self):
        from gui.impl.lobby.new_year.marketplace.ny_marketplace_view import NyMarketplaceView
        return NyMarketplaceView(self.__mainView.viewModel.marketplaceModel, self.__mainView)

    def __loadFriends(self):
        from gui.impl.lobby.new_year.friends.ny_friends_view import NyFriendsView
        return NyFriendsView(self.__mainView.viewModel.friendsModel, self.__mainView)

    def __loadChallenge(self):
        from gui.impl.lobby.new_year.challenge.ny_challenge import NewYearChallenge
        return NewYearChallenge(self.__mainView.viewModel.challengeModel, self.__mainView)

    def __loadFriendGlade(self):
        from gui.impl.lobby.new_year.friend_glade.ny_friend_glade_view import NyFriendGladeView
        return NyFriendGladeView(self.__mainView.viewModel.friendGladeModel, self.__mainView)

    def __loadFriendChallenge(self):
        from gui.impl.lobby.new_year.friend_challenge.ny_friend_challenge_view import NyFriendChallengeView
        return NyFriendChallengeView(self.__mainView.viewModel.friendChallengeModel, self.__mainView)

    @staticmethod
    def __makeSubModel(viewAlias, loader, customPredicate=None):
        return _SubModelInfo(viewAlias, loader(), customPredicate)
