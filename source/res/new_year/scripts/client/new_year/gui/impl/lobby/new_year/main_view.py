# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/main_view.py
import logging
import weakref
from functools import partial
import typing
import BigWorld
from Event import Event
from HeroTank import HeroTank
from cgf_components.view_camera_sync import IViewCameraSync, CameraState
from frameworks.wulf import ViewFlags, ViewSettings
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.main_view_model import MainViewModel, MainViews, SwitchStates
from new_year.gui.impl.lobby.new_year.ny_currency_panel_component import NyCurrencyPanelComponent
from new_year.gui.impl.lobby.new_year.ny_menu_component import NYMainMenu
from new_year.gui.impl.lobby.new_year.ny_sidebar_component import NYSidebar
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.new_year.sounds import NY_MAIN_VIEW_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showHeroTankPreview
from helpers import dependency, uniprof
from new_year.gui.shared.events import NewYearEvent
from new_year.ny_constants import NyWidgetTopMenu, InternalViewState
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from new_year.skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from new_year.gui.shared.event_dispatcher import NYViewCtx
_SubModelInfo = typing.NamedTuple('_SubModelInfo', [('ID', int), ('presenter', HistorySubModelPresenter), ('canBeLoaded', typing.Optional[typing.Callable[[], bool]])])
_STAGE_ENABLED_TAB = (NyWidgetTopMenu.CITY,
 NyWidgetTopMenu.SURPRISE_MACHINE,
 NyWidgetTopMenu.PET,
 NyWidgetTopMenu.QUESTS)
_logger = logging.getLogger(__name__)

class MainView(ViewImpl, IViewCameraSync):
    __slots__ = ('__ctx', '__backCallback', '__contentPresentersMap', '__componentPresenters', '__preCtx', '__regionName', '__internalState', '__skipCameraFlightOnClose')
    _COMMON_SOUND_SPACE = NY_MAIN_VIEW_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __appLoader = dependency.descriptor(IAppLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)

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
        self.__cameraState = CameraState.NOT_EXIST
        self.__skipCameraFlightOnClose = True
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
        if content is not None:
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

    def getInternalViewState(self):
        return self.__internalState

    def setInternalViewState(self, internalViewState, skipFight=None):
        _logger.debug('setInternalViewState %s', internalViewState)
        if self.__internalState != internalViewState:
            self.__internalState = internalViewState
            self.onInternalViewStateChanged(internalViewState, skipFight)

    def setCameraState(self, cameraState):
        _logger.debug('setCameraState %s', cameraState)
        self.__cameraState = cameraState
        if cameraState == CameraState.IN_TRANSITION:
            self.viewModel.setSwitchState(SwitchStates.WITH_SWITCHING_OBJS)
        if cameraState == CameraState.INSTALLED:
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
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': False}), EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onClose += self.__onCloseClick
        self.viewModel.onFadeInDone += self.__onFadeInDone
        self.viewModel.backButton.onBack += self.__onBackClicked
        self.__nyController.onStateChanged += self.__onStateChanged
        self.__nyController.onUIControlsLockChanged += self.__onUIControlsLockChanged
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated, scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.addListener(NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def _onLoading(self, *args, **kwargs):
        self.__registerSubModels()
        for presenter in self.__componentPresenters:
            presenter.initialize()

        g_eventBus.addListener(NewYearEvent.UPDATE_BACK_BUTTON, self.__onBackButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.setIsAnimatedShow(not kwargs['ctx'].kwargs.get('forceShowMainView', False))
        self.__switchSubView(self.__ctx)
        self.viewModel.setIsControlsLocked(self.__nyController.isUIControlsLocked())

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
        self.__nyController.onUIControlsLockChanged -= self.__onUIControlsLockChanged
        self.__hangarSpace.setVehicleSelectable(False)
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated, scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.removeListener(NewYearEvent.ON_PRE_SWITCH_VIEW, self.__onPreSwitchViewEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(NewYearEvent.UPDATE_BACK_BUTTON, self.__onBackButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': True}), EVENT_BUS_SCOPE.LOBBY)
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
        self.onNewYearViewInitialized.clear()
        return

    def __registerSubModels(self):
        self.__contentPresentersMap = _PresentersMap(self)
        self.__componentPresenters.extend([NYMainMenu(self.viewModel.mainMenu, weakref.proxy(self)), NYSidebar(self.viewModel.sidebar, weakref.proxy(self)), NyCurrencyPanelComponent(self.viewModel.currencyPanel, weakref.proxy(self))])

    def __onPreSwitchViewEvent(self, event):
        self.viewModel.setSwitchState(SwitchStates.DEFAULT)
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
                self.onNewYearViewInitialized(ctx.menuName)
                tx.setViewType(subModelInfo.ID)
            self.__ctx = ctx
            g_eventBus.handleEvent(NewYearEvent(NewYearEvent.ON_SWITCH_VIEW, ctx=self.__ctx), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def __onStateChanged(self):
        if not self.__nyController.isEnabled():
            self.__onClose()

    def __onClose(self):
        self.__skipCameraFlightOnClose = None
        NewYearNavigation.closeMainView(True)
        return

    def __onCloseClick(self):
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

    def __onUIControlsLockChanged(self, value):
        self.viewModel.setIsControlsLocked(value)


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
         NyWidgetTopMenu.QUESTS: partial(self.__makeSubModel, MainViews.TASKS, self.__loadQuests),
         NyWidgetTopMenu.SURPRISE_MACHINE: partial(self.__makeSubModel, MainViews.MACHINE, self.__loadSurpriseMachine),
         NyWidgetTopMenu.REWARDS: partial(self.__makeSubModel, MainViews.REWARDS, self.__loadRewards),
         NyWidgetTopMenu.PET: partial(self.__makeSubModel, MainViews.PET, self.__loadPet),
         NyWidgetTopMenu.INFO: partial(self.__makeSubModel, MainViews.INFO, self.__loadInfo)}

    def __loadCity(self):
        from new_year.gui.impl.lobby.new_year.city.ny_city_view import NyCityView
        return NyCityView(self.__mainView.viewModel.cityModel, self.__mainView)

    def __loadQuests(self):
        from new_year.gui.impl.lobby.new_year.quests.ny_quests_view import NyQuestsView
        return NyQuestsView(self.__mainView.viewModel.questsModel, self.__mainView)

    def __loadSurpriseMachine(self):
        from new_year.gui.impl.lobby.new_year.surprise_machine.surprise_machine_view import NySurpriseMachineView
        return NySurpriseMachineView(self.__mainView.viewModel.surpriseMachineModel, self.__mainView)

    def __loadRewards(self):
        from new_year.gui.impl.lobby.new_year.rewards_info.ny_rewards_info_view import NyRewardsInfoView
        return NyRewardsInfoView(self.__mainView.viewModel.rewardsModel, self.__mainView)

    def __loadPet(self):
        from new_year.gui.impl.lobby.new_year.pet.ny_pet_view import NyPetView
        return NyPetView(self.__mainView.viewModel.petModel, self.__mainView)

    def __loadInfo(self):
        from new_year.gui.impl.lobby.new_year.info_page.ny_info_view import NyInfoView
        return NyInfoView(self.__mainView.viewModel.infoModel, self.__mainView)

    @staticmethod
    def __makeSubModel(viewAlias, loader, customPredicate=None):
        return _SubModelInfo(viewAlias, loader(), customPredicate)
