# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/pet/ny_pet_story_view.py
import SoundGroups
from helpers import dependency
from new_year.gui.impl.new_year.sounds import RaccoonStates, RACCOON_HISTORY_SOUND_SPACE, VideoStartStopHandler, Videos
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet_story_view_model import PetStoryViewModel
from new_year.gui.impl.lobby.new_year.quests.ny_quest_helper import getWeekFromStart
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from new_year.helpers.ny_helpers import showWebmVideoView
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from new_year.ny_constants import NY_TAMAGOTCHI_STORY_BUBLE
from new_year.skeletons.new_year import ITamagotchiDataProvider
from new_year_account_settings import setNYSettings

class PetStoryView(ViewImpl):
    __slots__ = ('__videoHandler',)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _COMMON_SOUND_SPACE = RACCOON_HISTORY_SOUND_SPACE
    STEP_OFFSET = 1
    LAST_PET_STORY_CARD = 7

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.PetStoryView(), flags=ViewFlags.LOBBY_SUB_VIEW, model=PetStoryViewModel())
        self.__videoHandler = None
        super(PetStoryView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(PetStoryView, self).getViewModel()

    @classmethod
    def getCurrentWeekStep(cls):
        return max(1, min(getWeekFromStart() + cls.STEP_OFFSET, cls.LAST_PET_STORY_CARD))

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onCardInteract, self.__onCardInteract))

    def _initialize(self):
        super(PetStoryView, self)._initialize()
        week = self.getCurrentWeekStep()
        self._dataProvider.onUpdateTipsRequested(False)
        self.viewModel.setCurrentStep(week)
        setNYSettings(NY_TAMAGOTCHI_STORY_BUBLE, week)

    def _finalize(self):
        super(PetStoryView, self)._finalize()
        self._dataProvider.onUpdateTipsRequested(True)

    def __onClose(self):
        self.destroyWindow()

    @args2params(bool, bool)
    def __onCardInteract(self, enable, isVideoCard):
        state = RaccoonStates.CARDS if enable else RaccoonStates.HISTORY
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, state)
        if isVideoCard:
            self.__showVideo()

    def __showVideo(self):
        self.__videoHandler = VideoStartStopHandler(checkPauseOnStart=False)
        showWebmVideoView(videoSource=R.videos.new_year.pet.pet_story(), parent=self.getParentWindow(), onVideoStarted=self.__onVideoStarted, onVideoClosed=self.__onVideoClosed, isAutoClose=True, canEscape=True, isUIVisible=True, uiShowDelay=1)

    def __onVideoStarted(self):
        self.__videoHandler.onVideoStart(Videos.PET)

    def __onVideoClosed(self):
        self.__videoHandler.onVideoDone()
        self.__videoHandler = None
        self.viewModel.setIsVideoCardClosed(True)
        return


class PetStoryViewWindow(WindowImpl):

    def __init__(self, parent=None):
        super(PetStoryViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PetStoryView(), parent=parent)
