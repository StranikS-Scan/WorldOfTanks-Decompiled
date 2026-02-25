# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/lobby/video_view/video_view.py
import BigWorld
import SoundGroups
import Windowing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from cosmic_event.gui.configs.video_subs_config_reader import CosmicVideoSubsConfigReader
from cosmic_event.gui.impl.gen.view_models.views.lobby.video_view.video_view_model import VideoViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.video_view.video_view_subs_phrase_model import VideoViewSubsPhraseModel
from cosmic_sound import play2DSoundEvent, setCutSceneSoundGlobalEvent, IntroVideoSound, COSMIC_VIDEO_VIEW_SOUND_SPACE

class VideoView(ViewImpl):
    __slots__ = ('__videoName',)
    _COMMON_SOUND_SPACE = COSMIC_VIDEO_VIEW_SOUND_SPACE
    __DEFAULT_VOLUME = 0.5
    __VIDEO_RTPC_VOLUME_EVENT = 'RTPC_ext_volume_fader'

    def __init__(self, layoutID, videoName=''):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = VideoViewModel()
        super(VideoView, self).__init__(settings)
        self.__videoName = videoName

    @property
    def viewModel(self):
        return super(VideoView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(VideoView, self)._initialize(*args, **kwargs)
        self.__hideBack()

    def _finalize(self):
        self.__showBack()
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        super(VideoView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(VideoView, self)._onLoading(*args, **kwargs)
        self._updateModel()
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            model.setVideoName(self.__videoName)
            model.setDefaultVolume(self.__DEFAULT_VOLUME)
            phrasesArray = model.getPhrases()
            self.__fillPhrases(phrasesArray)

    def _getEvents(self):
        return ((self.viewModel.onVideoStarted, self.__onVideoStarted),
         (self.viewModel.onVideoPlay, self.__onVideoPlay),
         (self.viewModel.onVideoPause, self.__onVideoPause),
         (self.viewModel.currentVolume, self.__onCurrentVolume),
         (self.viewModel.onError, self.__onError),
         (self.viewModel.onClose, self.__onClose))

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        state = IntroVideoSound.PAUSE
        if isWindowAccessible:
            state = IntroVideoSound.RESUME
        setCutSceneSoundGlobalEvent(state)
        self.viewModel.setIsWindowAccessible(isWindowAccessible)

    def __fillPhrases(self, phrasesArrayModel):
        phrasesData = CosmicVideoSubsConfigReader.getIntroVideoPhrases()
        phrasesArrayModel.clear()
        phrasesArrayModel.reserve(len(phrasesData))
        for phraseData in phrasesData:
            phraseModel = VideoViewSubsPhraseModel()
            phraseModel.setStartTime(phraseData.startTime)
            phraseModel.setEndTime(phraseData.endTime)
            phraseText = R.strings.cosmicVideoSubs.introVideo.dyn(phraseData.text)()
            phraseModel.setText(backport.text(phraseText))
            phrasesArrayModel.addViewModel(phraseModel)

        phrasesArrayModel.invalidate()

    def __hideBack(self):
        BigWorld.worldDrawEnabled(False)

    def __showBack(self):
        BigWorld.worldDrawEnabled(True)

    def __onVideoStarted(self):
        soundGroupInstance = SoundGroups.g_instance
        soundGroupInstance.updateVideoVolume()
        play2DSoundEvent(IntroVideoSound.START)

    def __onVideoPlay(self):
        play2DSoundEvent(IntroVideoSound.RESUME)

    def __onVideoPause(self):
        play2DSoundEvent(IntroVideoSound.PAUSE)

    def __onCurrentVolume(self, volumeData):
        volume = volumeData.get('volume', 0.5)
        SoundGroups.g_instance.setRTPC(self.__VIDEO_RTPC_VOLUME_EVENT, volume)

    def __onError(self):
        play2DSoundEvent(IntroVideoSound.STOP)

    def __onClose(self):
        play2DSoundEvent(IntroVideoSound.STOP)
        self.destroyWindow()


class VideoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, videoName='', parent=None):
        super(VideoViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=VideoView(R.views.cosmic_event.lobby.video_view.VideoView(), videoName=videoName), parent=parent, layer=WindowLayer.OVERLAY)
