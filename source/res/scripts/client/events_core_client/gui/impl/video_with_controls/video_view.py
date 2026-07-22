# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/gui/impl/video_with_controls/video_view.py
from collections import namedtuple
import typing as t
import BigWorld
import SoundGroups
from frameworks.wulf import ResourceDescriptor, ResourceType, ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen_utils import INVALID_RES_ID
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen.view_models.views.lobby.events_core_client.video_view.video_view_model import VideoViewModel
from sound_gui_manager import CommonSoundSpaceSettings
if t.TYPE_CHECKING:
    from frameworks.wulf import Command, Window
SoundSpacePrerequisites = namedtuple('SoundSpaceSettingsPrerequisites', ('entranceStates', 'exitStates'))
VideoPrerequisites = namedtuple('VideoPrerequisites', ('videoPath', 'subtitlesPath', 'isControlsVisible', 'isSubtitlesVisible', 'soundSpace'))
_DEFAULT_VIEW_SOUND_SPACE = CommonSoundSpaceSettings(name='GF_VIDEO_VIEW', entranceStates={'STATE_video_overlay': 'STATE_video_overlay_on'}, exitStates={'STATE_video_overlay': 'STATE_video_overlay_off'}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
_RTPC_VOLUME_MULTIPLIER_FOR_SOUND_CONTROL = 0.5

class VideoView(ViewImpl):
    __slots__ = ('__prerequisites',)
    _COMMON_SOUND_SPACE = _DEFAULT_VIEW_SOUND_SPACE

    def __init__(self, layoutID, prerequisites):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = VideoViewModel()
        if prerequisites.subtitlesPath != INVALID_RES_ID:
            settings.relatedResources.append(ResourceDescriptor(type=ResourceType.SUBTITLES, index=prerequisites.subtitlesPath))
        if prerequisites.soundSpace is not None:
            soundSpace = prerequisites.soundSpace
            self._COMMON_SOUND_SPACE.entranceStates = soundSpace.entranceStates
            self._COMMON_SOUND_SPACE.exitStates = soundSpace.exitStates
        super(VideoView, self).__init__(settings)
        self.__prerequisites = prerequisites
        return

    @property
    def viewModel(self):
        return super(VideoView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(VideoView, self)._initialize(*args, **kwargs)
        self.__hideBack()

    def _finalize(self):
        self.__showBack()
        super(VideoView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(VideoView, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            model.setVideoPath(self.__prerequisites.videoPath)
            model.setIsControlsVisible(self.__prerequisites.isControlsVisible)
            model.setIsSubtitlesVisible(self.__prerequisites.isSubtitlesVisible and self.__prerequisites.subtitlesPath != INVALID_RES_ID)
            volume = SoundGroups.g_instance.getMaxVolumeFromCategories(SoundGroups.USER_SETTINGS_CATEGORY_NAMES)
            if self.__prerequisites.isControlsVisible:
                volume *= _RTPC_VOLUME_MULTIPLIER_FOR_SOUND_CONTROL
            model.setInitialAudioVolume(volume)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    @staticmethod
    def __hideBack():
        BigWorld.worldDrawEnabled(False)

    @staticmethod
    def __showBack():
        BigWorld.worldDrawEnabled(True)

    def __onClose(self):
        self.destroyWindow()


class VideoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, prerequisites, parent=None):
        super(VideoViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=VideoView(R.views.lobby.events_core_client.video_view.VideoView(), prerequisites), parent=parent, layer=WindowLayer.OVERLAY)
