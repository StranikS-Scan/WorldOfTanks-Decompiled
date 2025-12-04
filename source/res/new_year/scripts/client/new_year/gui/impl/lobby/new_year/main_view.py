# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/main_view.py
import logging
import weakref
import typing
import BigWorld
from functools import partial
from Event import Event
from HeroTank import HeroTank
from cgf_components.hangar_camera_manager import HangarCameraManager, CameraMode
from cgf_components.view_camera_sync import IViewCameraSync, CameraState
from frameworks.wulf import ViewFlags, ViewSettings
from new_year.gui.impl.lobby.new_year.tooltips.ny_main_widget_tooltip import NyMainWidgetTooltip
from new_year.skeletons.new_year import INewYearEnvironmentSwitchController
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.main_view_model import MainViewModel, MainViews, SwitchStates
from new_year.gui.impl.lobby.new_year.ny_currency_panel_component import NyCurrencyPanelComponent
from new_year.gui.impl.lobby.new_year.ny_progress_widget_view import NyProgressWidgetView
from new_year.gui.impl.lobby.new_year.ny_menu_component import NYMainMenu
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.lobby.new_year.env_switcher.env_switcher_btn_tip import EnvSwitcherBtnTip
from new_year.gui.impl.new_year.sounds import NY_MAIN_VIEW_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showHeroTankPreview, showHangar
from helpers import dependency, uniprof
from new_year.gui.shared.events import NewYearEvent
from new_year.ny_constants import NyWidgetTopMenu, InternalViewState, InternalViewStateID
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from new_year.skeletons.new_year import INewYearController
from new_year.gui.shared.event_dispatcher import showNYProgressView
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from new_year.gui.shared.event_dispatcher import NYViewCtx
_SubModelInfo = typing.NamedTuple('_SubModelInfo', [('ID', int), ('presenter', HistorySubModelPresenter), ('canBeLoaded', typing.Optional[typing.Callable[[], bool]])])
_STAGE_ENABLED_TAB = (NyWidgetTopMenu.CITY, NyWidgetTopMenu.SURPRISE_MACHINE, NyWidgetTopMenu.PET)
_logger = logging.getLogger(__name__)

class MainView(ViewImpl, IViewCameraSync):
    __slots__ = ('__ctx', '__backCallback', '__contentPresentersMap', '__componentPresenters', '__preCtx', '__regionName', '__internalState', '__skipCameraFlightOnClose', '__tipWindow', '__prevStateID', '__stateID')
    _COMMON_SOUND_SPACE = NY_MAIN_VIEW_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __appLoader = dependency.descriptor(IAppLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)

    def __init__(self, *args, **kwargs):
        _logger.info('New Year Main view object created')
        settings = ViewSettings(R.views.new_year.lobby.new_year.MainView())
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
        self.onInternalViewStateChanged = Event()
        self.onNewYearViewInitialized = Event()
        self.__internalState = InternalViewState.DEFAULT
        self.__prevStateID = InternalViewStateID.DEFAULT
        self.__stateID = InternalViewStateID.DEFAULT
        self.__cameraState = CameraState.NOT_EXIST
        self.__skipCameraFlightOnClose = True
        self.__tipWindow = None
        super(MainView, self).__init__(settings)
        return

    def __del__(self):
        _logger.info('New Year Main view object deleted')

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentPresenter(self):
        return self.__contentPresentersMap[self.__ctx.menuName].presenter

    def createToolTipContent(self, event, contentID):
        content = self.currentPresenter.createToolTipContent(event, contentID)
        if event.contentID == R.views.new_year.lobby.new_year.tooltips.NyMainWidgetTooltip():
            return NyMainWidgetTooltip(event.getArgument('block'))
        elif content is not None:
            return content
        else:
            for presenter in self.__componentPresenters:
                content = presenter.createToolTipContent(event, contentID)
                if content is not None:
                    return content

            return

    def createToolTip(self, event):
        return self.currentPresenter.createToolTip(event) or super(MainView, self).createToolTip(event)

    def createPopOverContent(self, event):
        return self.currentPresenter.createPopOverContent(event) or super(MainView, self).createPopOverContent(event)

    def createPopOver(self, event):
        return self.currentPresenter.createPopOver(event) or super(MainView, self).createPopOver(event)

    def getInternalViewState(self):
        return self.__internalState

    def setInternalViewState(self, internalViewState, skipFight=None):
        _logger.debug('setInternalViewState %s', internalViewState)
        if self.__internalState != internalViewState:
            self.__stateID = InternalViewStateID.stateToID(internalViewState, self.__stateID)
            self.__prevStateID = InternalViewStateID.stateToID(self.__internalState, self.__prevStateID)
            self.__internalState = internalViewState
            self.onInternalViewStateChanged(internalViewState, skipFight)

    def setCameraState(self, cameraState):
        _logger.debug('setCameraState %s', cameraState)
        if self.__prevStateID == self.__stateID == InternalViewStateID.TREE:
            if self.currentPresenter is not None:
                self.currentPresenter.setCameraSubState(self.__internalState, cameraState)
            return
        else:
            self.__cameraState = cameraState
            if cameraState == CameraState.IN_TRANSITION:
                self.viewModel.setSwitchState(SwitchStates.WITH_SWITCHING_OBJS)
            elif cameraState == CameraState.INSTALLED:
                self.viewModel.setSwitchState(SwitchStates.DONE)
            if self.currentPresenter is not None:
                self.currentPresenter.setCameraState(cameraState)
            return

    @property
    def skipCameraFlightOnInit(self):
        return self.__ctx.kwargs.get('skipFlight', None) if self.__ctx else None

    @property
    def skipCameraFlightOnClose(self):
        return self.__skipCameraFlightOnClose

    def _initialize(self, *args, **kwargs):
        NewYearNavigation.toggleHangarVehicleSelection(False)
        HangarCameraManager.forbidState(CameraMode.DEFAULT)
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': False}), EVENT_BUS_SCOPE.LOBBY)

    def _onLoading(self, *args, **kwargs):
        self.__registerSubModels()
        for presenter in self.__componentPresenters:
            presenter.initialize()

        self.viewModel.setIsAnimatedShow(not kwargs['ctx'].kwargs.get('forceShowMainView', False))
        self.__switchSubView(self.__ctx, True)
        self.viewModel.setIsControlsLocked(self.__nyController.isUIControlsLocked())
        self.__registerEnvSwitcherButtonTip()
        super(MainView, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        nextTick(partial(self.__hangarSpace.setVehicleSelectable, True))()
        nextTick(partial(self.__onStateChanged))()

    def _finalize(self):
        super(MainView, self)._finalize()
        HangarCameraManager.allowState(CameraMode.DEFAULT)
        if dependency.instance(IHangarSpace).spaceInited:
            BigWorld.worldDrawEnabled(True)
        self.__hangarSpace.setVehicleSelectable(False)
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': True}), EVENT_BUS_SCOPE.LOBBY)
        for presenter in self.__componentPresenters:
            presenter.finalize()
            presenter.clear()

        self.__componentPresenters = []
        self.currentPresenter.finalize()
        self.currentPresenter.clearTabCache()
        self.currentPresenter.clearNavigationHistory()
        self.__skipCameraFlightOnClose = self.currentPresenter.skipCameraFlightOnClose
        if self.__regionName:
            uniprof.exitFromRegion(self.__regionName)
        for subModelInfo in self.__contentPresentersMap.itervalues():
            subModelInfo.presenter.clear()

        self.__contentPresentersMap.clear()
        NewYearNavigation.clear()
        self.__backCallback = None
        self.onNewYearViewInitialized.clear()
        if self.__tipWindow:
            self.__onTipClosed()
        NewYearNavigation.resetHangarUI()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseClick),
         (self.viewModel.onFadeInDone, self.__onFadeInDone),
         (self.viewModel.backButton.onBack, self.__onBackClicked),
         (self.viewModel.onRewardInfo, self.__showProgress),
         (self.__nyController.onStateChanged, self.__onStateChanged),
         (self.__nyController.onUIControlsLockChanged, self.__onUIControlsLockChanged),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene))

    def _getListeners(self):
        return ((CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated, EVENT_BUS_SCOPE.DEFAULT), (NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, EVENT_BUS_SCOPE.LOBBY), (NewYearEvent.UPDATE_BACK_BUTTON, self.__onBackButtonUpdated, EVENT_BUS_SCOPE.LOBBY))

    def __registerSubModels(self):
        self.__contentPresentersMap = _PresentersMap(self)
        self.__componentPresenters.extend([NYMainMenu(self.viewModel.mainMenu, weakref.proxy(self)), NyCurrencyPanelComponent(self.viewModel.currencyPanel, weakref.proxy(self)), NyProgressWidgetView(self.viewModel.progressWidgetModel, weakref.proxy(self))])

    def __onPreSwitchViewEvent(self, event):
        if self.__preCtx is not None:
            return
        else:
            NewYearNavigation.setIsSceneInFade(True)
            self.viewModel.setSwitchState(SwitchStates.DEFAULT)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)
            self.__preCtx = event.ctx
            return

    def __onFadeInDone(self):
        if self.__preCtx is not None:
            self.__switchSubView(self.__preCtx)
            self.viewModel.setSwitchState(SwitchStates.DONE)
            self.__preCtx = None
        NewYearNavigation.setIsSceneInFade(False)
        return

    def __switchSubView(self, ctx, isLoadedFromHangar=False):
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
            showImmediately = ctx.kwargs.pop('isLoadedFromHangar', isLoadedFromHangar)
            subModelInfo.presenter.initialize(showImmediately, tabName=ctx.tabName, *ctx.args, **ctx.kwargs)
            self.onNewYearViewInitialized(ctx.menuName)
            self.viewModel.setViewType(subModelInfo.ID)
            ctx.kwargs['skipFlight'] = self.__ctx.kwargs.get('skipFlight') or subModelInfo.presenter.skipCameraFlightOnInit
            self.__ctx = ctx
            g_eventBus.handleEvent(NewYearEvent(NewYearEvent.ON_SWITCH_VIEW, ctx=self.__ctx), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def __onStateChanged(self):
        if not self.__nyController.isEnabled():
            self.__onClose()

    def __onClose(self):
        self.__skipCameraFlightOnClose = None
        showHangar()
        return

    def __onCloseClick(self):
        self.__onClose()

    def __showProgress(self):
        showNYProgressView(self.getParentWindow())

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

    def __onUIControlsLockChanged(self, value):
        self.viewModel.setIsControlsLocked(value)

    def __registerEnvSwitcherButtonTip(self):
        if self.__nyEnvSwitcherController.needToShowTip and self.__nyController.isOnboardingFinished():
            self.__tipWindow = EnvSwitcherBtnTip(mainView=False)
            self.setChildView(R.views.new_year.lobby.new_year.EnvSwitcherBtnTip(), self.__tipWindow)
            self.__tipWindow.onTipClosed += self.__onTipClosed
            self.viewModel.cityModel.setShowEnvSwitcherTip(True)

    def __onTipClosed(self):
        self.__tipWindow.onTipClosed -= self.__onTipClosed
        self.__tipWindow = None
        self.viewModel.cityModel.setShowEnvSwitcherTip(False)
        return

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onMouseOver3dScene(args):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': bool(args.get('isOver3dScene'))}))


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
        return {NyWidgetTopMenu.CITY: partial(self.__makeSubModel, MainViews.CITY, self.__loadCity),
         NyWidgetTopMenu.PET: partial(self.__makeSubModel, MainViews.PET, self.__loadPet),
         NyWidgetTopMenu.LEADERS: partial(self.__makeSubModel, MainViews.LEADERS, self.__loadLeaders),
         NyWidgetTopMenu.SURPRISE_MACHINE: partial(self.__makeSubModel, MainViews.MACHINE, self.__loadSurpriseMachine),
         NyWidgetTopMenu.INFO: partial(self.__makeSubModel, MainViews.INFO, self.__loadInfo)}

    def __loadCity(self):
        from new_year.gui.impl.lobby.new_year.city.ny_city_view import NyCityView
        return NyCityView(self.__mainView.viewModel.cityModel, self.__mainView)

    def __loadSurpriseMachine(self):
        from new_year.gui.impl.lobby.new_year.surprise_machine.surprise_machine_view import NySurpriseMachineView
        return NySurpriseMachineView(self.__mainView.viewModel.surpriseMachineModel, self.__mainView)

    def __loadPet(self):
        from new_year.gui.impl.lobby.new_year.pet.ny_pet_view import NyPetView
        return NyPetView(self.__mainView.viewModel.petModel, self.__mainView)

    def __loadLeaders(self):
        from new_year.gui.impl.lobby.new_year.leaderboard.ny_leaderboard_view import NewYearLeaderboardView
        return NewYearLeaderboardView(self.__mainView.viewModel.leaderboardModel, self.__mainView)

    def __loadInfo(self):
        from new_year.gui.impl.lobby.new_year.info_page.ny_info_view import NyInfoView
        return NyInfoView(self.__mainView.viewModel.infoModel, self.__mainView)

    @staticmethod
    def __makeSubModel(viewAlias, loader, customPredicate=None):
        return _SubModelInfo(viewAlias, loader(), customPredicate)
