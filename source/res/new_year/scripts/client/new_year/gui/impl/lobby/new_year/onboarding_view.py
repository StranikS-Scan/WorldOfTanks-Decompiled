# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/onboarding_view.py
import logging
from enum import Enum
from functools import partial
import BigWorld
import CGF
import GUI
from adisp import adisp_process
from Event import Event
from cgf_components.view_camera_sync import IViewCameraSync, CameraState
from frameworks.wulf import ViewFlags, ViewSettings
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from chat_shared import SYS_MESSAGE_TYPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.loot_box.loot_box_sounds import PausedSoundManager, LootBoxVideos, LootBoxVideoStartStopHandler
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.Scaleform.managers.fade_manager import FadeManager
from gui.shared.gui_items.processors.common import RequestSingleTokenProcessor
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showVideoView
from gui.server_events.bonuses import getAllNonQuestBonuses
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from new_year_common.items.components.ny_constants import ONBOARDING_QUEST_ID, TOKEN_NY25_MANDARIN, NewYearObjects
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
from new_year.gui.impl.new_year.sounds import NY_MAIN_VIEW_SOUND_SPACE
from new_year.gui.shared.event_dispatcher import showNYLevelUpWindow
from new_year.gui.shared.gui_items.processors.ny_processor import UpgradeCustomizationObjectLevel
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year.gui.shared.ny_level_helper import parseNYLevelToken
from new_year.ny_constants import CustomizationObjects, ANCHOR_TO_OBJECT, InternalViewState
from new_year.skeletons.new_year import INewYearController
_logger = logging.getLogger(__name__)

class OnboardingView(ViewImpl, IViewCameraSync):
    __slots__ = ('__currentObject', '__currencyProvider', '__objectConfig', '__hoveredObject', '__fadeManager', '__internalStateController', '__callback', '__levelRewards', '__cameraState', '__videoStartStopHandler')
    _COMMON_SOUND_SPACE = NY_MAIN_VIEW_SOUND_SPACE
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __appLoader = dependency.descriptor(IAppLoader)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __REWARD_INTERVAL = 1
    __FIRST_LEVEL = 1
    __ZONE = CustomizationObjects.FIR

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.OnboardingView())
        settings.args = args
        settings.kwargs = kwargs
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = OnboardingViewModel()
        self.__appLoader.getApp().setBackgroundAlpha(0.0)
        self.onInternalViewStateChanged = Event()
        self.__callback = None
        self.__cameraState = CameraState.NOT_INSTALLED
        self.__config = getNewYearGeneralConfig()
        self.__currencyProvider = NyCurrencyProvider()
        self.__currentObject = None
        self.__hoveredObject = HoverObject(None)
        self.__levelRewards = None
        self.__objectConfig = getNewYearObjectsConfig()
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler(checkPauseOnStart=False)
        super(OnboardingView, self).__init__(settings)
        self.__fadeManager = FadeManager()
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
        g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': False}), EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onClose += self.__onBack
        self.__nyController.onStateChanged += self.__onStateChanged
        self.__internalStateController.init()
        self.__fadeManager.setup()

    def _onLoading(self, *args, **kwargs):
        super(OnboardingView, self)._onLoading(*args, **kwargs)
        self.__currentObject = NewYearNavigation.getCurrentObject()
        giftCount = 0
        quest = self.__eventsCache.getQuestByID(ONBOARDING_QUEST_ID)
        firstEntranceToken = self.__config.getFirstEntranceToken()
        if quest is not None and not quest.isCompleted() and firstEntranceToken:
            self.__giveGift(firstEntranceToken)
            giftCount = int(quest.getRawBonuses().get('tokens', {}).get(TOKEN_NY25_MANDARIN, {}).get('count', 0))
        currency = giftCount + self.__currencyProvider.getCurrencyCount(NyCurrencyType.MANDARIN)
        with self.viewModel.transaction() as model:
            if not self.__nyController.isFirstEntrance():
                self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_PANORAMA, skipFight=True)
                model.setCurrentState(OnboardingState.PANORAMA)
                self.__realPurchase()
            else:
                self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_DEFAULT)
                model.setCurrentState(OnboardingState.DEFAULT)
            self.__updateMarkerInfo(model, currency)
            model.setAnimationCurrency(giftCount)
            model.backButton.setIsVisible(True)
            model.backButton.setCaption(backport.text(R.strings.ny.closeButton.MainView()))
            self.__fillCurrency(model.currencyPanel, currency)
        return

    @adisp_process
    def __giveGift(self, firstEntranceToken):
        result = yield RequestSingleTokenProcessor(firstEntranceToken).request()
        if not result.success:
            _logger.error('[NYOnboarding] gift not credited %s', result.userMsg)

    def _onLoaded(self, *args, **kwargs):
        super(OnboardingView, self)._onLoaded(*args, **kwargs)
        nextTick(partial(self.__hangarSpace.setVehicleSelectable, True))()
        nextTick(partial(self.__onStateChanged))()

    def _finalize(self):
        super(OnboardingView, self)._finalize()
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
        self.viewModel.onClose -= self.__onBack
        self.__nyController.onStateChanged -= self.__onStateChanged
        self.__internalStateController.fini()
        self.__fadeManager.destroy()
        if self.__nyController.isOnboardingFinished():
            return
        else:
            if self.__hoveredObject.isHovered:
                self.__getMarkerModel(self.__hoveredObject.objectName).setIsZoneHovered(False)
            destroyGUIHoveredObject(self.__hoveredObject)
            NewYearNavigation.clear()
            if dependency.instance(IHangarSpace).spaceInited:
                BigWorld.worldDrawEnabled(True)
            self.__hangarSpace.setVehicleSelectable(False)
            g_eventBus.handleEvent(events.LobbyHeaderEvent(events.LobbyHeaderEvent.TOGGLE_VISIBILITY, ctx={'visible': True}), EVENT_BUS_SCOPE.LOBBY)
            return

    def _getEvents(self):
        return ((self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onHoverMarker, self.__onHoverMarker),
         (self.viewModel.onHoverOutMarker, self.__onHoverOutMarker),
         (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene),
         (self.viewModel.onLevelUp, self.__onLevelUp),
         (self.viewModel.backButton.onBack, self.__onBack),
         (self.__nyController.onSpaceObjectHover, self.__onSpaceObjectHover),
         (self.__nyController.onGUIObjectHover, self.__onGUIObjectHover),
         (self.__currencyProvider.onCurrencyUpdated, self.__onCurrencyUpdated),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdate),
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
            if self.__callback is None:
                self.__rewardOpen()
            return

    def __updateMarkerInfo(self, model, currency):
        modelMarker = self.__getMarkerModel(self.__ZONE, model=model)
        modelMarker.customizationZone.setValue(CustomizationZone(self.__ZONE))
        modelMarker.setCurrentLevel(0)
        modelMarker.setCurrencyCount(currency)
        modelMarker.setLevelUpCurrencyNeed(self.__objectConfig.getNextLevelPrice(self.__ZONE, 0))

    def __onCurrencyUpdated(self, currency):
        if currency != NyCurrencyType.MANDARIN:
            return
        currencyCount = self.__currencyProvider.getCurrencyCount(NyCurrencyType.MANDARIN)
        if self.viewModel.currency.getValue() == currencyCount:
            return
        with self.viewModel.currencyPanel.transaction() as model:
            self.__fillCurrency(model, currencyCount)
            self.__getMarkerModel(self.__ZONE, model=model).setCurrencyCount(currencyCount)

    def __fillCurrency(self, model, currency):
        items = model.getItems()
        items.clear()
        itemModel = model.getItemsType()()
        itemModel.currency.setValue(NyCurrencyType.MANDARIN)
        itemModel.setAmount(currency)
        itemModel.setAllowClick(False)
        items.addViewModel(itemModel)
        items.invalidate()

    def __onUpdate(self, *_, **__):
        newObject = NewYearNavigation.getCurrentObject()
        if self.__currentObject == newObject or self.viewModel.getCurrentState() == OnboardingState.PANORAMA:
            return
        self.__currentObject = newObject
        if self.__currentObject == self.__ZONE:
            self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_FIR)
            self.viewModel.setCurrentState(OnboardingState.FIR)
        else:
            self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_DEFAULT)
            self.viewModel.setCurrentState(OnboardingState.DEFAULT)

    def __onStateChanged(self):
        if not self.__nyController.isEnabled():
            NewYearNavigation.closeMainView(True)

    def __onBack(self):
        state = self.viewModel.getCurrentState()
        if state == OnboardingState.DEFAULT:
            NewYearNavigation.closeMainView(True)
            return
        if state == OnboardingState.FIR:
            NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW)
            self.__currentObject = NewYearNavigation.getCurrentObject()
            self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_DEFAULT)
            self.viewModel.setCurrentState(OnboardingState.DEFAULT)

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
        currencyCount = self.__currencyProvider.getCurrencyCount(NyCurrencyType.MANDARIN)
        firstLevelPrice = self.__objectConfig.getNextLevelPrice(self.__ZONE, 0)
        if currencyCount < firstLevelPrice:
            return
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_FIRST_ENTRANCE: False})
        animatorMgr = CGF.getManager(self.__hangarSpace.space.getSpaceID(), NewYearAnimatorManager)
        duration = animatorMgr.startZoneAnimator(CustomizationObjects.FIR)
        self.__callback = BigWorld.callback(duration if duration else 0, self.__showVideo)

    @adisp_process
    def __showVideo(self):
        self.__callback = None
        self.viewModel.setCurrentState(OnboardingState.PANORAMA)
        yield self.__fadeManager.startFade()
        showVideoView(R.videos.new_year.onboarding_complete(), onVideoClosed=self.__onVideoClosed, onVideoStarted=self.__onVideoStarted, isAutoClose=True, soundControl=PausedSoundManager(), canEscape=False, isUIVisible=True, uiShowDelay=3)
        return

    def __onVideoStarted(self):
        self.__videoStartStopHandler.onVideoStart(LootBoxVideos.ONBOARDING)

    @adisp_process
    def __onVideoClosed(self):
        self.__videoStartStopHandler.onVideoDone()
        self.__internalStateController.setOnboardingState(_OnboardingState.ONBOARDING_PANORAMA, skipFight=True)
        yield self.__fadeManager.startFade(fadeIn=False)
        self.__realPurchase()

    @adisp_process
    def __realPurchase(self):
        result = yield UpgradeCustomizationObjectLevel(self.__ZONE).request()
        if result.success:
            self.__callback = BigWorld.callback(self.__REWARD_INTERVAL, self.__rewardOpen)
        else:
            _logger.error('[NYOnboarding] Fir upgrade failed: %s', result.userMsg)

    def __rewardOpen(self):
        self.__callback = None
        self.__nyController.onOnboardingFinished()
        if self.__levelRewards:
            showNYLevelUpWindow(useQueue=False, blurBackground=True, worldDrawEnabled=True, completedLevels=self.__levelRewards.keys(), levelRewards=self.__levelRewards, backCallback=lambda : NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW))
        return

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
    _PANORAMA_CAMERA_CHANGE_W = 1366
    __slots__ = ('__internalState', '__cameraState', '__viewModel', '__updateStateHandler', '__appWidth')

    def __init__(self, viewModel, updateStateHandler):
        self.__viewModel = viewModel
        self.__internalState = None
        self.__cameraState = CameraState.NOT_INSTALLED
        self.__updateStateHandler = updateStateHandler
        self.__appWidth = GUI.screenResolution()[:2][0]
        return

    def init(self):
        g_eventBus.addListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onResize, scope=EVENT_BUS_SCOPE.GLOBAL)

    def fini(self):
        g_eventBus.removeListener(events.GameEvent.CHANGE_APP_RESOLUTION, self.__onResize, scope=EVENT_BUS_SCOPE.GLOBAL)
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
            self.__setInternalViewState(self.__getPanoramaState(), skipFight)
        else:
            self.__setInternalViewState(onboardingState.value, skipFight)

    def setInternalViewState(self, internalViewState, skipFight=None):
        raise NYSoftException('It is forbidden to set the state directly, use setOnboardingState')

    def __onResize(self, event):
        ctx = event.ctx
        if 'width' in ctx and 'height' in ctx:
            self.__appWidth = ctx['width']
            if self.__internalState in (InternalViewState.ONBOARDING_PANORAMA, InternalViewState.ONBOARDING_PANORAMA_SMALL):
                self.__setInternalViewState(self.__getPanoramaState(), True)

    def __getPanoramaState(self):
        return InternalViewState.ONBOARDING_PANORAMA if self.__appWidth > self._PANORAMA_CAMERA_CHANGE_W else InternalViewState.ONBOARDING_PANORAMA_SMALL

    def __setInternalViewState(self, internalViewState, skipFight=None):
        if self.__internalState != internalViewState:
            self.__internalState = internalViewState
            self.__updateStateHandler(internalViewState, skipFight)
