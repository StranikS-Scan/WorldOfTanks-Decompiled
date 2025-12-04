# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/onboarding_view.py
import BigWorld
import logging
import CGF
from enum import Enum
from functools import partial
from adisp import adisp_process
from Event import Event
from cgf_components.hangar_camera_manager import HangarCameraManager, CameraMode
from cgf_components.view_camera_sync import IViewCameraSync, CameraState
from frameworks.wulf import ViewFlags, ViewSettings
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from chat_shared import SYS_MESSAGE_TYPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.Scaleform.Waiting import Waiting
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.gui_items.processors.common import RequestSingleTokenProcessor
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showHangar
from gui.shared.utils.graphics import isRendererPipelineDeferred
from gui.server_events.bonuses import getAllNonQuestBonuses
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from new_year.gui.impl.lobby.new_year.env_switcher.ny_environment_switcher_controller import EnvironmentState
from new_year.helpers.ny_helpers import showWebmVideoView
from new_year_common.items.components.ny_constants import ONBOARDING_QUEST_ID, TOKEN_MANDARIN, NewYearObjects
from new_year_common.ny_exception import NYSoftException
from shared_utils import nextTick, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.server_events import IEventsCache
from new_year.cgf.ny_animations import NewYearAnimatorManager
from new_year.helpers.server_settings import getNewYearObjectsConfig, getNewYearGeneralConfig
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZone
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_view_model import NyCityViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.onboarding_view_model import OnboardingViewModel, OnboardingState
from new_year.gui.impl.lobby.new_year.ny_views_helpers import HoverObject, destroyGUIHoveredObject
from new_year.gui.impl.lobby.new_year.tooltips.ny_currency_tooltip import NyCurrencyTooltip
from new_year.gui.impl.lobby.new_year.tooltips.customization_zone_tooltip import CustomizationZoneTooltip
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.new_year.sounds import NY_MAIN_VIEW_SOUND_SPACE, VideoStartStopHandler, Videos
from new_year.gui.shared.event_dispatcher import showNYLevelUpWindow
from new_year.gui.shared.gui_items.processors.ny_processor import UpgradeCustomizationObjectLevel
from new_year.gui.shared.ny_level_helper import parseNYLevelToken
from new_year.ny_constants import CustomizationObjects, ANCHOR_TO_OBJECT, InternalViewState
from new_year.skeletons.new_year import INewYearController, INewYearCurrencyController, INewYearEnvironmentSwitchController
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
_logger = logging.getLogger(__name__)

class OnboardingView(ViewImpl, IViewCameraSync):
    __slots__ = ('__objectConfig', '__hoveredObject', '__internalStateController', '__levelRewards', '__cameraState', '__videoHandler', '__blur', '__config', '__pendingGiftCount', '__video')
    _COMMON_SOUND_SPACE = NY_MAIN_VIEW_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __appLoader = dependency.descriptor(IAppLoader)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)
    __REWARD_INTERVAL = 1
    __FIRST_LEVEL = 1
    __ZONE = CustomizationObjects.FIR
    __WAITING_LBL = 'synchronizeOnboardingRewards'
    __WAIT_MANDARINS_ID = 'onboardingMandarinReward'
    __DEFAULT_LEVEL = 0
    __NEXT_LEVEL = __DEFAULT_LEVEL + 1

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.OnboardingView())
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = OnboardingViewModel()
        self.__appLoader.getApp().setBackgroundAlpha(0.0)
        self.onInternalViewStateChanged = Event()
        self.__cameraState = CameraState.NOT_INSTALLED
        self.__config = getNewYearGeneralConfig()
        self.__hoveredObject = HoverObject(None)
        self.__levelRewards = None
        self.__blur = None
        self.__objectConfig = getNewYearObjectsConfig()
        self.__videoHandler = None
        self.__pendingGiftCount = 0
        self.__video = None
        super(OnboardingView, self).__init__(settings)
        self.__internalStateController = _InternalViewStateController(self.viewModel, self.onInternalViewStateChanged)
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyCurrencyTooltip():
            currency = NyCurrencyType(event.getArgument('currency'))
            return NyCurrencyTooltip(NyCurrencyType(currency), allowClick=False)
        else:
            return CustomizationZoneTooltip(event.getArgument('customizationZone')) if contentID == R.views.new_year.lobby.new_year.tooltips.CustomizationZoneTooltip() else None

    @property
    def viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        super(OnboardingView, self)._initialize(*args, **kwargs)
        NewYearNavigation.toggleHangarVehicleSelection(False)
        HangarCameraManager.forbidState(CameraMode.DEFAULT)
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': False}), EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onClose += self.__onBack
        self.__nyController.onStateChanged += self.__onStateChanged
        self.__internalStateController.init()

    def _onLoading(self, *args, **kwargs):
        super(OnboardingView, self)._onLoading(*args, **kwargs)
        self.__pendingGiftCount = 0
        quest = self.__eventsCache.getQuestByID(ONBOARDING_QUEST_ID)
        firstEntranceToken = self.__config.getFirstEntranceToken()
        if quest is not None and not quest.isCompleted() and firstEntranceToken:
            self.__pendingGiftCount = int(quest.getRawBonuses().get('tokens', {}).get(TOKEN_MANDARIN, {}).get('count', 0))
        currency = self.__pendingGiftCount + self.__nyCurrencyController.getMandarinTokenCount
        with self.viewModel.transaction() as model:
            model.setAnimationCurrency(self.__pendingGiftCount)
            self.__updateMarkerInfo(model, currency)
            self.__fillCurrency(model.currencyPanel, currency)
            if not self.__nyController.isFirstEntrance():
                self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_PANORAMA, skipFight=True)
                model.setCurrentState(OnboardingState.PANORAMA)
                self.__realPurchase()
            else:
                self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_DEFAULT)
                model.setCurrentState(OnboardingState.DEFAULT)
                model.setIsFirstShow(True)
                self.__showVideo()
            model.backButton.setIsVisible(True)
            model.backButton.setCaption(backport.text(R.strings.ny.closeButton.MainView()))
        return

    @adisp_process
    def __giveGift(self, firstEntranceToken):
        Waiting.show(self.__WAIT_MANDARINS_ID)
        result = yield RequestSingleTokenProcessor(firstEntranceToken).request()
        if not result.success:
            Waiting.hide(self.__WAIT_MANDARINS_ID)
            _logger.error('[NYOnboarding] gift not credited %s', result.userMsg)

    def _onLoaded(self, *args, **kwargs):
        super(OnboardingView, self)._onLoaded(*args, **kwargs)
        nextTick(partial(self.__hangarSpace.setVehicleSelectable, True))()
        nextTick(partial(self.__onStateChanged))()

    def _finalize(self):
        super(OnboardingView, self)._finalize()
        HangarCameraManager.allowState(CameraMode.DEFAULT)
        self.viewModel.onClose -= self.__onBack
        self.__nyController.onStateChanged -= self.__onStateChanged
        self.__internalStateController.fini()
        if self.__nyController.isOnboardingFinished():
            return
        else:
            if self.__video is not None:
                self.__stopVideo(destroy=True)
            if Waiting.isOpened(self.__WAITING_LBL):
                Waiting.hide(self.__WAITING_LBL)
            Waiting.hide(self.__WAIT_MANDARINS_ID)
            if self.__hoveredObject.isHovered:
                self.__getMarkerModel(self.__hoveredObject.objectName).setIsZoneHovered(False)
            destroyGUIHoveredObject(self.__hoveredObject)
            NewYearNavigation.clear()
            if dependency.instance(IHangarSpace).spaceInited:
                BigWorld.worldDrawEnabled(True)
            self.__hangarSpace.setVehicleSelectable(False)
            self.__onHideBlur()
            g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': True}), EVENT_BUS_SCOPE.LOBBY)
            NewYearNavigation.resetHangarUI()
            return

    def _getEvents(self):
        return ((self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onHoverMarker, self.__onHoverMarker),
         (self.viewModel.onHoverOutMarker, self.__onHoverOutMarker),
         (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene),
         (self.viewModel.onHideBlur, self.__onHideBlur),
         (self.viewModel.onLevelUp, self.__onLevelUp),
         (self.viewModel.backButton.onBack, self.__onBack),
         (self.__nyController.onSpaceObjectHover, self.__onSpaceObjectHover),
         (self.__nyController.onGUIObjectHover, self.__onGUIObjectHover),
         (self.__nyCurrencyController.onCurrencyUpdated, self.__onCurrencyUpdated),
         (g_messengerEvents.serviceChannel.onChatMessageReceived, self.__onChatMessageReceived))

    def __onChatMessageReceived(self, *args):
        message = args[1]
        if message is None or message.type != SYS_MESSAGE_TYPE.tokenQuests.index() or not message.data:
            return
        else:
            questID = first((questID for questID in message.data.get('completedQuestIDs', set()) if parseNYLevelToken(questID) == self.__FIRST_LEVEL))
            if not questID:
                return
            self.__levelRewards = {self.__FIRST_LEVEL: getAllNonQuestBonuses(message.data.get('detailedRewards', {}).get(questID, {}))}
            self.__rewardOpen()
            return

    def __updateMarkerInfo(self, model, currency):
        modelMarker = self.__getMarkerModel(self.__ZONE, model=model)
        currentLevel = self.__DEFAULT_LEVEL
        toysCount = len(NewYearAtmospherePresenter.getNewYearLevelToys(self.__ZONE, self.__NEXT_LEVEL))
        atmospherePointsCount = NewYearAtmospherePresenter.getNewYearLevelAtmospherePoints(self.__ZONE, self.__NEXT_LEVEL)
        modelMarker.customizationZone.setValue(CustomizationZone(self.__ZONE))
        modelMarker.setCurrentLevel(currentLevel)
        modelMarker.setCurrencyCount(currency)
        modelMarker.setLevelUpCurrencyNeed(self.__objectConfig.getNextLevelPrice(self.__ZONE, 0))
        modelMarker.setAtmospherePoints(atmospherePointsCount)
        modelMarker.setToysCount(toysCount)

    def __onCurrencyUpdated(self, currency, _):
        if currency != NyCurrencyType.MANDARIN:
            return
        currencyCount = self.__nyCurrencyController.getMandarinTokenCount
        with self.viewModel.transaction() as model:
            self.__fillCurrency(model.currencyPanel, currencyCount)
            self.__updateMarkerInfo(model, currencyCount)
        Waiting.hide(self.__WAIT_MANDARINS_ID)
        self.__enableFirState()

    def __fillCurrency(self, model, currency):
        items = model.getItems()
        items.clear()
        itemModel = model.getItemsType()()
        itemModel.currency.setValue(NyCurrencyType.MANDARIN)
        itemModel.setAmount(currency)
        itemModel.setAllowClick(False)
        items.addViewModel(itemModel)
        items.invalidate()

    def __onStateChanged(self):
        if not self.__nyController.isEnabled():
            NewYearNavigation.closeMainView()

    def __onHideBlur(self):
        if self.__blur:
            self.__blur.fini()
            self.__blur = None
        return

    def __onBack(self):
        state = self.viewModel.getCurrentState()
        if state == OnboardingState.DEFAULT:
            NewYearNavigation.closeMainView()
            return
        if state == OnboardingState.FIR:
            NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW)
            self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_DEFAULT)
            self.viewModel.setCurrentState(OnboardingState.DEFAULT)
        self.__onHideBlur()

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

    def __onLevelUp(self):
        currencyCount = self.__nyCurrencyController.getMandarinTokenCount
        firstLevelPrice = self.__objectConfig.getNextLevelPrice(self.__ZONE, 0)
        if currencyCount < firstLevelPrice:
            return
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_FIRST_ENTRANCE: False})
        animatorMgr = CGF.getManager(self.__hangarSpace.space.getSpaceID(), NewYearAnimatorManager)
        animatorMgr.startZoneAnimator(CustomizationObjects.FIR)
        self.__realPurchase()

    def __showVideo(self):
        self.__videoHandler = VideoStartStopHandler(checkPauseOnStart=False)
        onboardingVideo = R.videos.new_year.onboarding.onboarding_day() if self.__nyEnvSwitcherController.currentAppliedDayNightMode == EnvironmentState.DAY else R.videos.new_year.onboarding.onboarding_night()
        self.__video = showWebmVideoView(videoSource=onboardingVideo, onVideoStarted=self.__onVideoStarted, onVideoClosed=self.__onVideoClosed, isAutoClose=True, canEscape=True, isUIVisible=True, uiShowDelay=3)

    def __onVideoStarted(self):
        onboardingSound = Videos.ONBOARDING_DAY if self.__nyEnvSwitcherController.currentAppliedDayNightMode == EnvironmentState.DAY else Videos.ONBOARDING_NIGHT
        self.__videoHandler.onVideoStart(onboardingSound)

    def __onVideoClosed(self):
        if self.__videoHandler is None:
            return
        else:
            self.__stopVideo()
            firstEntranceToken = self.__config.getFirstEntranceToken()
            if self.__pendingGiftCount > 0 and firstEntranceToken:
                self.__giveGift(firstEntranceToken)
            else:
                currentTokens = self.__nyCurrencyController.getMandarinTokenCount
                with self.viewModel.transaction() as model:
                    self.__updateMarkerInfo(model, currentTokens)
                    self.__fillCurrency(model.currencyPanel, currentTokens)
                self.__enableFirState()
            return

    def __stopVideo(self, destroy=False):
        self.__videoHandler.onVideoDone()
        self.__videoHandler = None
        if destroy:
            self.__video.destroy()
        self.__video = None
        return

    def __enableFirState(self):
        with self.viewModel.transaction() as model:
            self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_FIR, skipFight=True)
            model.setCurrentState(OnboardingState.FIR)
            if model.getAnimationCurrency() > 0:
                self.__blur = CachedBlur(enabled=True, ownLayer=self.layer, blurRadius=0.4)

    @adisp_process
    def __realPurchase(self):
        Waiting.show(self.__WAITING_LBL)
        result = yield UpgradeCustomizationObjectLevel(self.__ZONE).request()
        if not result.success:
            Waiting.hide(self.__WAITING_LBL)
            _logger.error('[NYOnboarding] Fir upgrade failed: %s', result.userMsg)
            showHangar()

    def __rewardOpen(self):
        self.__nyController.onOnboardingFinished()
        Waiting.hide(self.__WAITING_LBL)
        if self.__levelRewards:
            showNYLevelUpWindow(useQueue=False, blurBackground=isRendererPipelineDeferred(), worldDrawEnabled=True, completedLevels=self.__levelRewards.keys(), levelRewards=self.__levelRewards, backCallback=lambda : NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW))

    @args2params(str)
    def __onHoverMarker(self, markerName):
        self.__nyController.setGuiObjectHover(markerName, True)

    @args2params(str)
    def __onHoverOutMarker(self, markerName):
        self.__nyController.setGuiObjectHover(markerName, False)

    def __onSpaceObjectHover(self, objectName, isHovered):
        objectName = ANCHOR_TO_OBJECT.get(objectName, '')
        if objectName == self.__ZONE:
            self.__hoveredObject.setSpaceObjectHover(objectName, isHovered)
            self.__getMarkerModel(objectName).setIsZoneHovered(self.__hoveredObject.isHovered)

    def __onGUIObjectHover(self, objectName, isHovered):
        if objectName == self.__ZONE:
            self.__hoveredObject.setGUIObjectHover(objectName, isHovered)

    @replaceNoneKwargsModel
    def __getMarkerModel(self, objectName, model=None):
        return getattr(model, objectName.lower() + 'Marker')

    def getInternalViewState(self):
        return self.__internalStateController.getInternalViewState()

    def setInternalViewState(self, internalViewState, skipFight=None):
        pass

    def setCameraState(self, cameraState):
        self.__internalStateController.setCameraState(cameraState)

    @property
    def skipCameraFlightOnClose(self):
        return self.__internalStateController.skipCameraFlightOnClose

    @property
    def skipCameraFlightOnInit(self):
        return self.__internalStateController.skipCameraFlightOnInit


class _OnboardingState(Enum):
    ONBOARDING_DEFAULT = 'onboarding_default'
    ONBOARDING_FIR = 'onboarding_fir'
    ONBOARDING_PANORAMA = 'onboarding_panorama'


class _InternalViewStateController(IViewCameraSync):
    __slots__ = ('__internalState', '__cameraState', '__viewModel', '__updateStateHandler')

    def __init__(self, viewModel, updateStateHandler):
        self.__viewModel = viewModel
        self.__internalState = None
        self.__cameraState = CameraState.NOT_INSTALLED
        self.__updateStateHandler = updateStateHandler
        return

    def init(self):
        pass

    def fini(self):
        self.__updateStateHandler = None
        self.__viewModel = None
        return

    def setCameraState(self, cameraState):
        _logger.debug('setCameraState %s', cameraState)
        self.__cameraState = cameraState
        self.__viewModel.setCameraState(self.__cameraState)

    @property
    def skipCameraFlightOnInit(self):
        return False

    @property
    def skipCameraFlightOnClose(self):
        return True

    def getInternalViewState(self):
        return self.__internalState

    def setOnboardingState(self, onboardingState, skipFight=None):
        if onboardingState == _OnboardingState.ONBOARDING_PANORAMA:
            self.__setInternalViewState(InternalViewState.ONBOARDING_PANORAMA, skipFight)
        else:
            self.__setInternalViewState(onboardingState.value, skipFight)

    def setInternalViewState(self, internalViewState, skipFight=None):
        raise NYSoftException('It is forbidden to set the state directly, use setOnboardingState')

    def __setInternalViewState(self, internalViewState, skipFight=None):
        if self.__internalState != internalViewState:
            self.__internalState = internalViewState
            self.__updateStateHandler(internalViewState, skipFight)
