# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/main_view.py
import json
import logging
import time
import typing
from account_helpers.AccountSettings import WotAnniversary15
from frameworks.state_machine import SingleStateObserver
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.event_model import EventType
from gui.impl.gen.view_models.views.lobby.wot_anniversary.main_view_model import MainViewModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.progression_step_model import ProgressionStepModel, ProgressionState
from gui.impl.gen.view_models.views.lobby.wot_anniversary.slot_model import SlotModel, SlotState
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.wot_anniversary.album_card_view import AlbumCardPresenter
from gui.impl.lobby.wot_anniversary.content_loader.models import BackgroundID, VIDEOS_CONTENT_NAME
from gui.impl.lobby.wot_anniversary.sound_helper import getMainSoundSpace
from gui.impl.lobby.wot_anniversary.state_machine.machine import WotAnniversaryStateMachine
from gui.impl.lobby.wot_anniversary.state_machine.states import WotAnniversaryStateID
from gui.impl.lobby.wot_anniversary.tooltips.progression_box_tooltip import ProgressionBoxTooltip
from gui.impl.lobby.wot_anniversary.tooltips.simple_tooltip_view import SimpleTooltip
from gui.impl.lobby.wot_anniversary.wot_anniversary_helpers import setWotAnniversarySetting, getWotAnniversarySetting, pushErrorSysMessage
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency, time_utils
from shared_utils import findFirst, nextTick
from skeletons.gui.wot_anniversary import IWotAnniversaryController
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from gui.impl.lobby.wot_anniversary.content_loader.models import BackgroundContent, VideosContent
    from gui.impl.gen.view_models.views.lobby.wot_anniversary.media_resource_model import MediaResourceModel
_logger = logging.getLogger(__name__)
_FIRST_PAGE_LAST_DAY_ID = 12
_MAX_ENVELOPE_ANIMATION_COUNT = 3

class MainView(ViewImpl):
    _COMMON_SOUND_SPACE = getMainSoundSpace()
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.MainView(), model=MainViewModel(), args=args, kwargs=kwargs)
        self.__flowMachine = WotAnniversaryStateMachine(self, _FIRST_PAGE_LAST_DAY_ID)
        self.__content = None
        self.__cardPresenter = None
        super(MainView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wot_anniversary.tooltips.SimpleTooltip():
            return SimpleTooltip(event.getArgument('payload', ''))
        return ProgressionBoxTooltip(int(event.getArgument('boxIndex', 0))) if contentID == R.views.lobby.wot_anniversary.tooltips.ProgressionBoxTooltip() else super(MainView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onOpenInfoPage, self.__onOpenInfoPage),
         (self.viewModel.onOpenCardPreview, self.__onOpenCardPreview),
         (self.viewModel.onOpenEnvelope, self.__onOpenEnvelope),
         (self.viewModel.onOpenRewardScreen, self.__onOpenRewardScreen),
         (self.viewModel.onSetAnimationDisabled, self.__onSetAnimationDisabled),
         (self.viewModel.onSecondPageOpened, self.__onSecondPageOpened),
         (self.__wotAnniversaryController.onEndDateReached, self.__onEndDateReached),
         (self.__wotAnniversaryController.onSettingsChanged, self.__onSettingsChanged))

    def _getCallbacks(self):
        return (('tokens', self.__onTokensUpdated),)

    @wg_async
    def _onLoading(self, *args, **kwargs):
        super(MainView, self)._onLoading(*args, **kwargs)
        self.__cardPresenter = AlbumCardPresenter(self.viewModel.envelopeCard, self, self.__closeCardPreview)
        self.__flowMachine.configure()
        for observer in (MainRequestStateObserver(self, WotAnniversaryStateID.MAIN_REQUEST),
         AlbumRequestSuccessStateObserver(self, WotAnniversaryStateID.ALBUM_REQUEST_SUCCESS),
         AlbumRequestFailedStateObserver(self, WotAnniversaryStateID.ALBUM_REQUEST_FAILED),
         RewardRegularStateObserver(self, WotAnniversaryStateID.REWARD_REGULAR),
         SimpleAlbumStateObserver(self, WotAnniversaryStateID.REWARD_PROGRESSION),
         AlbumProgressionIncreaseCounterStateObserver(self, WotAnniversaryStateID.ALBUM_PROGRESSION_INCREASE_COUNTER),
         AlbumSlotUnlockStateObserver(self, WotAnniversaryStateID.ALBUM_SLOT_UNLOCK),
         AlbumProgressionStageUnlockStateObserver(self, WotAnniversaryStateID.ALBUM_PROGRESSION_STAGE_UNLOCK),
         AlbumFirstPageEndedStateObserver(self, WotAnniversaryStateID.ALBUM_FIRST_PAGE_ENDED),
         MainFinalStateObserver(self, WotAnniversaryStateID.MAIN_FINAL)):
            self.__flowMachine.connect(observer)

        self.__flowMachine.start()
        self.__fillModel()
        contentCache = self.__wotAnniversaryController.cdnCacheMgr
        if not contentCache.isSynced():
            self.viewModel.setResourceLoading(True)
            yield wg_await(contentCache.waitSync())
            if self.__isDestroyed():
                return
            self.viewModel.setResourceLoading(False)
        self.__content = contentCache.getAlbumContent()
        if self.__content is None:
            _logger.warning('Dynamic content is not downloaded.')
            pushErrorSysMessage()
            nextTick(self.destroyWindow)()
            return
        else:
            self.__fillDynamicContent()
            return

    def _finalize(self):
        self.__destroyCardPresenter()
        self.__flowMachine.stop()
        self.__flowMachine = None
        self.__content = None
        super(MainView, self)._finalize()
        return

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillCommonData(model=tx)
            self.__fillSlots(model=tx)
            self.__fillProgression(model=tx)

    @replaceNoneKwargsModel
    def __fillDynamicContent(self, model=None):
        for contentKey, mediaResourceModel in zip((BackgroundID.FIRST_PAGE, BackgroundID.SECOND_PAGE), (model.firstFilledOverlay, model.secondFilledOverlay)):
            if contentKey in self.__content:
                self.__fillMediaResourceModel(mediaResourceModel, self.__content[contentKey])

        if VIDEOS_CONTENT_NAME in self.__content:
            videos = self.__content[VIDEOS_CONTENT_NAME]
            model.videos.setConversionOneEnv(videos.conversionOneEnv)
            model.videos.setConversionTwoEnvs(videos.conversionTwoEnvs)
            model.videos.setConversionThreeEnvs(videos.conversionThreeEnvs)
            model.videos.setTurnPage(videos.turnPage)
        slots = model.getSlots()
        for slot in slots:
            dayContent = self.__content.get(str(slot.getDayId() + 1))
            slot.setVideo(dayContent.video if dayContent is not None else '')

        slots.invalidate()
        return

    @staticmethod
    def __fillMediaResourceModel(model, content):
        model.setSmall(content.small)
        model.setMedium(content.medium)
        model.setLarge(content.large)
        model.setExtraLarge(content.extraLarge)

    @replaceNoneKwargsModel
    def __fillCommonData(self, model=None):
        config = self.__wotAnniversaryController.config
        model.setStartDate(config.startDate)
        model.setEndDate(config.endDate)
        model.setAnimationDisabled(getWotAnniversarySetting(WotAnniversary15.IS_ALBUM_ANIMATIONS_DISABLED))

    @replaceNoneKwargsModel
    def __fillSlots(self, model=None):
        config = self.__wotAnniversaryController.config
        dayTokenCount = self.__wotAnniversaryController.getDayTokenCount()
        nextToOpenDayID = dayTokenCount + 1
        currentTime = time_utils.getServerUTCTime()
        lastSeenDate = getWotAnniversarySetting(WotAnniversary15.ALBUM_LAST_SEEN_DATE)
        content = self.__content or {}
        maxAnimationCount = _MAX_ENVELOPE_ANIMATION_COUNT
        slots = model.getSlots()
        slots.clear()
        for dayIdx, dayConfig in enumerate(config.days):
            dayID = dayIdx + 1
            dayContent = content.get(str(dayID))
            openDate = config.startDate + time_utils.ONE_DAY * dayIdx
            if openDate > currentTime:
                state = SlotState.LOCKED
                isAnimationRequired = False
            elif dayID <= dayTokenCount:
                state = SlotState.FILL
                isAnimationRequired = False
            elif dayID == nextToOpenDayID:
                state = SlotState.READY
                isAnimationRequired = lastSeenDate <= openDate
            else:
                state = SlotState.AVAILABLE
                isAnimationRequired = lastSeenDate <= openDate
            if isAnimationRequired and maxAnimationCount > 0:
                maxAnimationCount -= 1
            else:
                isAnimationRequired = False
            slot = SlotModel()
            slot.setState(state)
            slot.setDayId(dayIdx)
            slot.setLabel(str(dayIdx + config.firstDayLabel))
            slot.setOpenTimestamp(openDate)
            slot.setSpecial(dayConfig.isSpecial)
            slot.setInitialAnimationRequired(isAnimationRequired)
            slot.setVideo(dayContent.video if dayContent is not None else '')
            slots.addViewModel(slot)

        slots.invalidate()
        setWotAnniversarySetting(WotAnniversary15.ALBUM_LAST_SEEN_DATE, currentTime)
        return

    @replaceNoneKwargsModel
    def __fillProgression(self, model=None):
        config = self.__wotAnniversaryController.config
        progressionTokenCount = self.__wotAnniversaryController.getProgressionTokenCount()
        steps = model.getProgressionSteps()
        steps.clear()
        previousTokenCount = 0
        for step in config.progression:
            requiredTokenCount = step.tokenCount - previousTokenCount
            if progressionTokenCount >= requiredTokenCount:
                actualTokenCount = requiredTokenCount
                state = ProgressionState.RECEIVED
            elif progressionTokenCount < 0:
                actualTokenCount = 0
                state = ProgressionState.LOCKED
            else:
                actualTokenCount = progressionTokenCount
                state = ProgressionState.IN_PROGRESS
            stepModel = ProgressionStepModel()
            stepModel.setState(state)
            stepModel.setActual(actualTokenCount)
            stepModel.setRequired(requiredTokenCount)
            steps.addViewModel(stepModel)
            previousTokenCount = step.tokenCount
            progressionTokenCount -= requiredTokenCount

        steps.invalidate()

    def __onOpenInfoPage(self):
        showBrowserOverlayView(self.__wotAnniversaryController.config.infoPageUrl, alias=VIEW_ALIAS.BROWSER_OVERLAY, parent=self.getParentWindow())

    @args2params(int, bool)
    def __onOpenCardPreview(self, dayId, isFlow):
        _logger.info('Open Card Preview dayId=%d, isFlow=%s', dayId, isFlow)
        if isFlow:
            self.__flowMachine.postEnvelopePreviewEvent(dayId)
        if self.__cardPresenter is None or self.__cardPresenter.isLoaded:
            return
        else:
            with self.viewModel.transaction() as tx:
                tx.setEnvelopeCardOpened(True)
                tx.setBlur(True)
            self.__cardPresenter.initialize(dayId, isFlow)
            return

    def __closeCardPreview(self, isFlow):
        if self.__isDestroyed() or self.__cardPresenter is None:
            return
        else:
            if isFlow:
                self.__flowMachine.postStateEvent()
            self.__cardPresenter.finalize()
            with self.viewModel.transaction() as tx:
                tx.setEnvelopeCardOpened(False)
                tx.setBlur(False)
            return

    def __destroyCardPresenter(self):
        if self.__cardPresenter is None:
            return
        else:
            self.__cardPresenter.finalize()
            self.__cardPresenter.clear()
            self.__cardPresenter = None
            return

    def __onOpenEnvelope(self):
        self.__runFlow()

    def __runFlow(self):
        if self.__flowMachine.isFinalStateReached():
            self.__flowMachine.restart()
        self.__flowMachine.postMainRequestEvent()

    def __onOpenRewardScreen(self):
        self.__flowMachine.postStateEvent()

    def __onSecondPageOpened(self):
        self.__flowMachine.postStateEvent()

    @args2params(bool)
    def __onSetAnimationDisabled(self, value):
        setWotAnniversarySetting(WotAnniversary15.IS_ALBUM_ANIMATIONS_DISABLED, value)
        with self.viewModel.transaction() as tx:
            tx.setAnimationDisabled(value)

    def __onTokensUpdated(self, diff):
        if self.viewModel.getInteractionBlock():
            return
        config = self.__wotAnniversaryController.config
        if config.progressionToken in diff:
            self.__fillProgression()
        if config.dayToken in diff:
            self.__fillSlots()

    def __onSettingsChanged(self):
        if not self.__wotAnniversaryController.isEnabled():
            self.destroyWindow()

    def __onEndDateReached(self):
        self.destroyWindow()

    def __onClose(self):
        isInteractionBlocked = self.viewModel.getInteractionBlock()
        if self.viewModel.getEnvelopeCardOpened():
            self.__closeCardPreview(isInteractionBlocked)
            return
        if isInteractionBlocked:
            return
        self.destroyWindow()

    def __isDestroyed(self):
        return self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING) or self.viewModel is None


class _MainViewObserver(SingleStateObserver):

    def __init__(self, view, stateID):
        self.__view = view
        super(_MainViewObserver, self).__init__(stateID)

    def clear(self):
        self.__view = None
        return

    @property
    def albumView(self):
        return self.__view


class MainRequestStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            tx.setInteractionBlock(True)
            tx.setEnvelopeOpening(True)

    def onExitState(self, event=None):
        self.albumView.viewModel.setEnvelopeOpening(False)


class AlbumRequestSuccessStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            tx.event.setEventType(EventType.INVOICE_PROCESSED)
            tx.event.setPayload(json.dumps({'timeStamp': time.time()}))


class AlbumRequestFailedStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            tx.event.setEventType(EventType.INVOICE_REJECTED)
            tx.event.setPayload(json.dumps({'timeStamp': time.time()}))


class RewardRegularStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        self.albumView.viewModel.setBlur(True)

    def onExitState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            tx.setBlur(False)
            tx.event.setEventType(EventType.REGULAR_REWARDS_RECEIVED)
            tx.event.setPayload(json.dumps({'timeStamp': time.time()}))


class SimpleAlbumStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        self.albumView.viewModel.setBlur(True)

    def onExitState(self, event=None):
        self.albumView.viewModel.setBlur(False)


class AlbumProgressionIncreaseCounterStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            steps = tx.getProgressionSteps()
            stepInProgress = findFirst(lambda s: s.getState() == ProgressionState.IN_PROGRESS, steps)
            if stepInProgress is None:
                return
            nextProgress = stepInProgress.getActual() + 1
            stepInProgress.setActual(nextProgress)
            if nextProgress == stepInProgress.getRequired():
                stepInProgress.setState(ProgressionState.RECEIVED)
            steps.invalidate()
        return


class AlbumSlotUnlockStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            slots = tx.getSlots()
            readySlot = findFirst(lambda s: s.getState() == SlotState.READY, slots)
            if readySlot is None:
                _logger.warning('Ready slot is not found.')
                return
            slots = tx.getSlots()
            readySlot.setState(SlotState.FILL)
            nextDayID = readySlot.getDayId() + 1
            if nextDayID < len(slots):
                nextSlot = slots.getValue(nextDayID)
                if nextSlot is not None and nextSlot.getState() == SlotState.AVAILABLE:
                    nextSlot.setState(SlotState.READY)
            slots.invalidate()
        return


class AlbumProgressionStageUnlockStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            steps = tx.getProgressionSteps()
            lockedStep = findFirst(lambda s: s.getState() == ProgressionState.LOCKED, steps)
            if lockedStep is None:
                return
            lockedStep.setState(ProgressionState.IN_PROGRESS)
            steps.invalidate()
        return


class AlbumFirstPageEndedStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        with self.albumView.viewModel.transaction() as tx:
            tx.event.setEventType(EventType.TURN_PAGE)
            tx.event.setPayload(json.dumps({'timeStamp': time.time()}))


class MainFinalStateObserver(_MainViewObserver):

    def onEnterState(self, event=None):
        self.albumView.viewModel.setInteractionBlock(False)


class MainWindow(LobbyWindow):

    def __init__(self, parent=None, **kwargs):
        super(MainWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=MainView(**kwargs), parent=parent)
