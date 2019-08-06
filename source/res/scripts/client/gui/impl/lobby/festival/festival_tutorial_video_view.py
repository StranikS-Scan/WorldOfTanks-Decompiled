# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_tutorial_video_view.py
from festivity.festival import sounds
from festivity.festival.sounds import FestivalSoundEvents
from frameworks.wulf import ViewFlags, Window, WindowFlags, WindowSettings
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_tutorial_video_view_model import FestivalTutorialVideoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl

class FestivalTutorialVideoView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(FestivalTutorialVideoView, self).__init__(R.views.lobby.festival.festival_tutorial_video_view.FestivalTutorialVideoView(), ViewFlags.VIEW, FestivalTutorialVideoViewModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(FestivalTutorialVideoView, self).getViewModel()

    def destroyWindow(self):
        self.__endSounds()
        super(FestivalTutorialVideoView, self).destroyWindow()

    def _initialize(self):
        super(FestivalTutorialVideoView, self)._initialize()
        self.viewModel.onCloseBtnClicked += self.__onCloseBtnClicked
        self.viewModel.onStartVideoPlaying += self.__onStartVideoPlaying
        self.viewModel.onStopVideoPlaying += self.__onStopVideoPlaying

    def _finalize(self):
        self.viewModel.onCloseBtnClicked -= self.__onCloseBtnClicked
        self.viewModel.onStartVideoPlaying -= self.__onStartVideoPlaying
        self.viewModel.onStopVideoPlaying -= self.__onStopVideoPlaying
        super(FestivalTutorialVideoView, self)._finalize()

    def __onCloseBtnClicked(self, *_):
        self.destroyWindow()

    def __endSounds(self):
        sounds.setSoundState(groupName=FestivalSoundEvents.FESTIVAL_TUTORIAL_VIDEO_GROUP, stateName=FestivalSoundEvents.FESTIVAL_TUTORIAL_VIDEO_STATE_EXIT)

    def __onStartVideoPlaying(self, *_):
        sounds.setSoundState(groupName=FestivalSoundEvents.FESTIVAL_TUTORIAL_VIDEO_GROUP, stateName=FestivalSoundEvents.FESTIVAL_TUTORIAL_VIDEO_STATE_ENTER, eventName=FestivalSoundEvents.FESTIVAL_TUTORIAL_VIDEO_EVENT_NAME)

    def __onStopVideoPlaying(self, *_):
        self.__endSounds()


class FestivalTutorialVideoViewWindow(Window):
    __slots__ = ('__blur',)

    def __init__(self, parent=None):
        settings = WindowSettings()
        settings.flags = WindowFlags.OVERLAY
        settings.content = FestivalTutorialVideoView()
        settings.parent = parent
        super(FestivalTutorialVideoViewWindow, self).__init__(settings)
        self.__blur = None
        return

    def _initialize(self):
        super(FestivalTutorialVideoViewWindow, self)._initialize()
        self.__blur = WGUIBackgroundBlurSupportImpl(blur3dScene=False)
        self.__blur.enable(APP_CONTAINERS_NAMES.DIALOGS, [APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.BROWSER,
         APP_CONTAINERS_NAMES.SYSTEM_MESSAGES])

    def _finalize(self):
        self.__blur.disable()
        super(FestivalTutorialVideoViewWindow, self)._finalize()
