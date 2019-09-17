# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar_event/offspring_concert_view.py
import logging
import BigWorld
from frameworks.wulf import ViewFlags
from gui.impl.gen.view_models.views.lobby.hangar_event.offspring_concert_view_model import OffspringConcertViewModel
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import LobbySimpleEvent
from gui.shared.main_wnd_state_watcher import ClientMainWindowStateWatcher
from hangar_music_stage.camera_mode import MusicStageCameraMode
from hangar_music_stage.sounds import TheOffspringSound, setSoundState, raiseSoundEvent, setRTPC
from helpers import dependency
from skeletons.hangar_music_stage import IOffspringConcertManager, IConcertView
from skeletons.gui.shared.utils import IHangarSpace
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
_CAMERA_INDEX_TO_NAME = {0: 'Camera2',
 1: 'Camera1',
 2: 'Camera3'}

class OffspringConcertView(ViewImpl, SoundViewMixin, IConcertView, ClientMainWindowStateWatcher):
    __slots__ = ('__cameraMode', '__registerDraggingCallbackID')
    __concertMgr = dependency.descriptor(IOffspringConcertManager)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, layoutID, initialCameraName='', renderEnvironment=''):
        super(OffspringConcertView, self).__init__(layoutID, ViewFlags.LOBBY_SUB_VIEW, OffspringConcertViewModel)
        self.__cameraMode = MusicStageCameraMode(initialCameraName, renderEnvironment)
        cameraIndex = findFirst(lambda k: _CAMERA_INDEX_TO_NAME[k] == initialCameraName, _CAMERA_INDEX_TO_NAME.iterkeys())
        if cameraIndex is not None:
            self.viewModel.setCurrentCameraIdx(cameraIndex)
        self.__registerDraggingCallbackID = None
        return

    @property
    def viewModel(self):
        return super(OffspringConcertView, self).getViewModel()

    def switchToSong(self, index):
        currentIdx = self.__getCurrentTrackIdx()
        if currentIdx != -1 and currentIdx != index:
            self.viewModel.setPreviousTrackIdx(currentIdx)
            self.viewModel.setCurrentTrackIdx(index)

    def onSongFinished(self, nextSongIdx):
        self.viewModel.setDesiredToSwitchTrackIdx(nextSongIdx)
        self.viewModel.setTriggerTrackFinishedAnimation(not self.viewModel.getTriggerTrackFinishedAnimation())

    def _initialize(self):
        super(OffspringConcertView, self)._initialize()
        self.__onEnterSound()
        self.__cameraMode.activate()
        rndTrackIndex = self.__concertMgr.concertViewStart(self)
        trackList = self.viewModel.getTracks()
        for track in self.__concertMgr.trackNames:
            trackList.addString(track)

        trackList.invalidate()
        if rndTrackIndex is not None:
            self.switchToSong(rndTrackIndex)
        self.viewModel.onCloseAction += self.__onCloseAction
        self.viewModel.onTrackClicked += self.__onTrackClicked
        self.viewModel.onTrackSwitched += self.__onTrackSwitched
        self.viewModel.onCameraBtnClicked += self.__onCameraBtnClicked
        self.viewModel.onCameraSwitched += self.__onCameraSwitched
        self.__registerDraggingCallbackID = BigWorld.callback(0.0, self.__registerDragging)
        self.__hangarSpace.onSpaceDestroy += self.__onHangarSpaceDestroy
        self.mainWindowWatcherInit()
        return

    def _finalize(self):
        self.mainWindowWatcherDestroy()
        self.__hangarSpace.onSpaceDestroy -= self.__onHangarSpaceDestroy
        if self.__registerDraggingCallbackID is not None:
            BigWorld.cancelCallback(self.__registerDraggingCallbackID)
            self.__registerDraggingCallbackID = None
        self.viewModel.onCloseAction -= self.__onCloseAction
        self.viewModel.onTrackClicked -= self.__onTrackClicked
        self.viewModel.onTrackSwitched -= self.__onTrackSwitched
        self.viewModel.onCameraBtnClicked -= self.__onCameraBtnClicked
        self.viewModel.onCameraSwitched -= self.__onCameraSwitched
        if self.__cameraMode is not None:
            self.__cameraMode.deactivate()
            self.__cameraMode = None
        self.__concertMgr.concertViewDone()
        self.__onExitSound()
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_OFF), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        return

    def __registerDragging(self):
        self.__registerDraggingCallbackID = None
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_ON), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        return

    def __onCloseAction(self):
        showHangar()

    def __onTrackClicked(self, args=None):
        if args is None:
            _logger.warning('Track index is not found')
            return
        else:
            trackIndex = args.get('index')
            if trackIndex is None:
                _logger.warning('Track index is not found')
                return
            self.viewModel.setDesiredToSwitchTrackIdx(trackIndex)
            self.__stopSongSoundEvent()
            return

    def __onTrackSwitched(self, args=None):
        trackIndex = self.__getDesiredToSwitchTrackIdx()
        if trackIndex == -1:
            _logger.warning('Track index is not found')
            return
        self.__concertMgr.onSongSwitched(trackIndex)

    def __onCameraBtnClicked(self, args=None):
        if args is None:
            _logger.warning('Camera index is not found')
            return
        else:
            cameraIndex = int(args.get('index', -1))
            if cameraIndex == -1:
                _logger.warning('Camera index is not found')
                return
            self.viewModel.setCurrentCameraIdx(cameraIndex)
            return

    def __onCameraSwitched(self, args=None):
        if args is None:
            _logger.warning('Camera index is not found')
            return
        else:
            cameraIndex = int(args.get('index', -1))
            if cameraIndex == -1:
                _logger.warning('Camera index is not found')
                return
            cameraName = _CAMERA_INDEX_TO_NAME.get(cameraIndex)
            if cameraName is None:
                _logger.warning('Could not find camera with index %i', cameraIndex)
                return
            self.__setConcertCameraSoundParam()
            self.__cameraMode.switchToCamera(cameraName)
            return

    def __onHangarSpaceDestroy(self, _):
        self.__onCloseAction()

    def __onEnterSound(self):
        raiseSoundEvent(TheOffspringSound.THE_OFFSPRING_CONCERT_EVENT_ENTER)
        setSoundState(TheOffspringSound.THE_OFFSPRING_CONCERT_STATE, TheOffspringSound.THE_OFFSPRING_CONCERT_STATE_ENTER)
        self.__setConcertCameraSoundParam()

    @staticmethod
    def __onExitSound():
        raiseSoundEvent(TheOffspringSound.THE_OFFSPRING_CONCERT_EVENT_EXIT)
        setSoundState(TheOffspringSound.THE_OFFSPRING_CONCERT_STATE, TheOffspringSound.THE_OFFSPRING_CONCERT_STATE_EXIT)

    @staticmethod
    def __stopSongSoundEvent():
        raiseSoundEvent(TheOffspringSound.THE_OFFSPRING_CONCERT_EVENT_STOP_SONG)

    def __setConcertCameraSoundParam(self):
        setRTPC('RTPC_off_concert_camera', self.__getCurrentCameraIdx())

    def __getCurrentCameraIdx(self):
        currentCameraIdx = self.viewModel.getCurrentCameraIdx()
        return -1 if currentCameraIdx is None else int(currentCameraIdx)

    def __getCurrentTrackIdx(self):
        currentTrackIndex = self.viewModel.getCurrentTrackIdx()
        return -1 if currentTrackIndex is None else int(currentTrackIndex)

    def __getDesiredToSwitchTrackIdx(self):
        desiredToSwitchTrackIdx = self.viewModel.getDesiredToSwitchTrackIdx()
        return -1 if desiredToSwitchTrackIdx is None else int(desiredToSwitchTrackIdx)

    def _onClientMainWindowStateChanged(self, isWindowVisible):
        if isWindowVisible:
            currentTrackId = self.__getCurrentTrackIdx()
            if currentTrackId != -1:
                self.__concertMgr.onSongSwitched(currentTrackId)
        else:
            self.__stopSongSoundEvent()

    def __onNotifyCursorDragging(self, event):
        isDragging = event.ctx.get('isDragging', False)
        self.viewModel.setIsDragging(isDragging)
