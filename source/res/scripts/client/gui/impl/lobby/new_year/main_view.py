# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/main_view.py
import weakref
from functools import partial
import typing
import BigWorld
from HeroTank import HeroTank
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.main_view_model import MainViewModel, MainViews, SwitchStates
from gui.impl.lobby.new_year.ny_menu_component import NYMainMenu
from gui.impl.lobby.new_year.ny_sidebar_component import NYSidebar
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NY_MAIN_VIEW_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showHeroTankPreview
from helpers import dependency, uniprof
from new_year.ny_constants import NyWidgetTopMenu
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.shared.event_dispatcher import NYViewCtx
_SubModelInfo = typing.NamedTuple('_SubModelInfo', [('ID', int), ('presenter', HistorySubModelPresenter), ('canBeLoaded', typing.Optional[typing.Callable[[], bool]])])
_STAGE_ENABLED_TAB = NyWidgetTopMenu.GLADE

class MainView(ViewImpl):
    __slots__ = ('__ctx', '__backCallback', '__contentPresentersMap', '__componentPresenters', '__preCtx', '__regionName')
    _COMMON_SOUND_SPACE = NY_MAIN_VIEW_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __appLoader = dependency.descriptor(IAppLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)

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
        return self.currentPresenter.createPopOverContent(event) or super(MainView, self).createPopOverContent(event)

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self.__onCloseClick
        self.viewModel.onFadeInDone += self.__onFadeInDone
        self.viewModel.backButton.onBack += self.__onBackClicked
        self.__nyController.onStateChanged += self.__onStateChanged
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated, scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.addListener(events.NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _onLoading(self, *args, **kwargs):
        self.__registerSubModels()
        for presenter in self.__componentPresenters:
            presenter.initialize()

        g_eventBus.addListener(events.NewYearEvent.UPDATE_BACK_BUTTON, self.__onBackButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.setIsAnimatedShow(not kwargs['ctx'].kwargs.get('forceShowMainView', False))
        self.viewModel.setIsGladeIntroActive(not self.__isGladeIntroVisited())
        self.__switchSubView(self.__ctx)

    def _onLoaded(self, *args, **kwargs):
        nextTick(partial(self.__hangarSpace.setVehicleSelectable, True))()
        nextTick(partial(self.__onStateChanged))()

    def _finalize(self):
        if dependency.instance(IHangarSpace).spaceInited:
            BigWorld.worldDrawEnabled(True)
        self.viewModel.onClose -= self.__onCloseClick
        self.viewModel.onFadeInDone -= self.__onFadeInDone
        self.viewModel.backButton.onBack -= self.__onBackClicked
        self.__nyController.onStateChanged -= self.__onStateChanged
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__hangarSpace.setVehicleSelectable(False)
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated, scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.removeListener(events.NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.NewYearEvent.UPDATE_BACK_BUTTON, self.__onBackButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        for presenter in self.__componentPresenters:
            presenter.finalize()
            presenter.clear()

        self.__componentPresenters = []
        self.currentPresenter.finalize()
        self.currentPresenter.clearTabCache()
        self.currentPresenter.clearNavigationHistory()
        if self.__regionName:
            uniprof.exitFromRegion(self.__regionName)
        for subModelInfo in self.__contentPresentersMap.itervalues():
            subModelInfo.presenter.clear()

        self.__contentPresentersMap.clear()
        NewYearNavigation.clear()
        self.__backCallback = None
        return

    def __registerSubModels(self):
        self.__contentPresentersMap = _PresentersMap(self)
        self.__componentPresenters.extend([NYMainMenu(self.viewModel.mainMenu, self), NYSidebar(self.viewModel.sidebar, self)])

    def __onPreSwitchViewEvent(self, event):
        if event.ctx.menuName == NyWidgetTopMenu.GLADE and not self.__isGladeIntroVisited():
            self.viewModel.setSwitchState(SwitchStates.TO_GLADE_WITH_INTRO)
        elif event.ctx.kwargs.get('isObjectSwitched', False):
            self.viewModel.setSwitchState(SwitchStates.WITH_SWITCHING_OBJS)
        else:
            self.viewModel.setSwitchState(SwitchStates.DEFAULT)
        subModelInfo = self.__contentPresentersMap[event.ctx.menuName]
        subModelInfo.presenter.preLoad(*event.ctx.args, **event.ctx.kwargs)
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)
        self.__preCtx = event.ctx

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
            if self.currentPresenter.isLoaded:
                self.currentPresenter.finalize()
            with self.viewModel.transaction() as tx:
                subModelInfo.presenter.initialize(tabName=ctx.tabName, *ctx.args, **ctx.kwargs)
                tx.setViewType(subModelInfo.ID)
            self.__ctx = ctx
            g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_SWITCH_VIEW, ctx=self.__ctx), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def __onStateChanged(self):
        if not self.__nyController.isEnabled():
            self.__onClose()

    def __onClose(self):
        NewYearNavigation.closeMainView(True)

    def __onCloseClick(self, args):
        self.__onClose()

    def __onBackButtonUpdated(self, event):
        self.__backCallback = event.ctx.get('callback')
        if not event.ctx.get('isVisible') and self.viewModel.backButton.getIsVisible() or self.__backCallback is None:
            self.__clearBackButton()
            return
        else:
            with self.viewModel.transaction() as model:
                model.backButton.setIsVisible(True)
                model.backButton.setCaption(event.ctx.get('caption', backport.text(R.strings.ny.backButton.label())))
                model.backButton.setGoTo(event.ctx.get('goTo', ''))
            return

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
        if NewYearStorageKeys.GLADE_INTRO_VISITED in diff:
            self.viewModel.setIsGladeIntroActive(not self.__isGladeIntroVisited())

    def __isGladeIntroVisited(self):
        return self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.GLADE_INTRO_VISITED, False)


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
         NyWidgetTopMenu.COLLECTIONS: partial(self.__makeSubModel, MainViews.COLLECTIONS, self.__loadAlbum),
         NyWidgetTopMenu.SHARDS: partial(self.__makeSubModel, MainViews.SHARDS, self.__loadDecorations),
         NyWidgetTopMenu.INFO: partial(self.__makeSubModel, MainViews.INFO, self.__loadInfo),
         NyWidgetTopMenu.REWARDS: partial(self.__makeSubModel, MainViews.REWARDS, self.__loadRewards),
         NyWidgetTopMenu.DECORATIONS: partial(self.__makeSubModel, MainViews.CRAFT_MACHINE, self.__loadCraftMachine)}

    def __loadGlade(self):
        from gui.impl.lobby.new_year.glade.ny_glade_view import NyGladeView
        return NyGladeView(self.__mainView.viewModel.gladeModel, self.__mainView)

    def __loadAlbum(self):
        from gui.impl.lobby.new_year.albums.ny_album_view import NyAlbumView
        return NyAlbumView(self.__mainView.viewModel.collectionsModel, self.__mainView)

    def __loadDecorations(self):
        from gui.impl.lobby.new_year.break_decorations.ny_break_decorations_view import NyBreakDecorationsView
        return NyBreakDecorationsView(self.__mainView.viewModel.shardsModel, self.__mainView)

    def __loadInfo(self):
        from gui.impl.lobby.new_year.info_page.ny_info_view import NyInfoView
        return NyInfoView(self.__mainView.viewModel.infoModel, self.__mainView)

    def __loadRewards(self):
        from gui.impl.lobby.new_year.rewards_info.ny_rewards_info_view import NyRewardsInfoView
        return NyRewardsInfoView(self.__mainView.viewModel.rewardsModel, self.__mainView)

    def __loadCraftMachine(self):
        from gui.impl.lobby.new_year.craft.ny_craft_view import NyCraftView
        return NyCraftView(self.__mainView.viewModel.craftMachineModel, self.__mainView)

    @staticmethod
    def __makeSubModel(viewAlias, loader, customPredicate=None):
        return _SubModelInfo(viewAlias, loader(), customPredicate)
