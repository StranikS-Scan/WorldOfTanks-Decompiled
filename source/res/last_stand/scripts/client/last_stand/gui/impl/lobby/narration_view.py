# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/narration_view.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from last_stand.gui.impl.gen.view_models.views.lobby.narration_view_model import NarrationViewModel
from frameworks.wulf import WindowFlags, WindowLayer
from last_stand.gui.impl.lobby.base_view import SwitcherPresenter
from last_stand.gui.impl.lobby.widgets.parallax_view import ParallaxView
from last_stand.gui.sounds import playSound
from gui.impl.pub.view_component import ViewComponent
from last_stand.gui.sounds.sound_constants import META_VOICEOVER_UNMUTE, META_VOICEOVER_BUTTON_CLICK_UNMUTE, META_VOICEOVER_MUTE, META_VOICEOVER_BUTTON_CLICK_MUTE, META_STORY_POINT_OPEN_SOUND, META_STORY_POINT_CLOSE_SOUND
from last_stand.gui import ls_account_settings
from helpers import dependency
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.skeletons.ls_story_point_controller import ILSStoryPointController

class NarrationView(ViewComponent[NarrationViewModel]):
    lsStoryPointCtrl = dependency.descriptor(ILSStoryPointController)
    LAYOUT_ID = R.views.last_stand.mono.lobby.narration_view()

    def __init__(self, layoutID=R.views.last_stand.mono.lobby.narration_view()):
        super(NarrationView, self).__init__(layoutID, NarrationViewModel)
        self.__currentSlideIndex = self.lsStoryPointCtrl.FIRST_STORY_POINT_INDEX

    @property
    def viewModel(self):
        return super(NarrationView, self).getViewModel()

    def _getChildComponents(self):
        return {R.aliases.last_stand.shared.Parallax(): ParallaxView,
         R.aliases.last_stand.shared.Switcher(): SwitcherPresenter}

    def _onLoading(self, *args, **kwargs):
        super(NarrationView, self)._onLoading(*args, **kwargs)
        self.__prepareSelectedStoryPoint()
        self.__fillViewModel()

    def _finalize(self):
        playSound(META_STORY_POINT_CLOSE_SOUND.format(self.__currentSlideIndex))
        self.lsStoryPointCtrl.selectedStoryPointID = None
        super(NarrationView, self)._finalize()
        return

    def _getEvents(self):
        return [(self.viewModel.onClose, self._onClose),
         (self.viewModel.onVoiceoverToggle, self.__onVoiceoverToggle),
         (self.viewModel.onSlide, self.__onSlide),
         (self.lsStoryPointCtrl.onStoryPointStatusUpdated, self.__onStoryPointStatusUpdated)]

    def _onClose(self):
        self.destroyWindow()

    def __onVoiceoverToggle(self):
        isMuted = ls_account_settings.getSettings(AccountSettingsKeys.STORY_POINT_VOICEOVER_MUTED)
        newStateMute = not isMuted
        ls_account_settings.setSettings(AccountSettingsKeys.STORY_POINT_VOICEOVER_MUTED, newStateMute)
        self.viewModel.setIsVoiceoverActive(not newStateMute)
        if newStateMute:
            playSound(META_VOICEOVER_MUTE)
            playSound(META_VOICEOVER_BUTTON_CLICK_MUTE)
        else:
            playSound(META_VOICEOVER_UNMUTE)
            playSound(META_VOICEOVER_BUTTON_CLICK_UNMUTE)

    def __onSlide(self, args):
        slideIndex = int(args.get('slideIndex', self.lsStoryPointCtrl.FIRST_STORY_POINT_INDEX))
        viewModel = self.viewModel
        viewModel.setSlideNumber(slideIndex)
        playSound(META_STORY_POINT_CLOSE_SOUND.format(self.__currentSlideIndex))
        playSound(META_STORY_POINT_OPEN_SOUND.format(slideIndex))
        self.__currentSlideIndex = slideIndex
        self.lsStoryPointCtrl.selectedStoryPointID = self.lsStoryPointCtrl.getStoryPointIDByIndex(slideIndex)
        self.__updateButtonLock(viewModel)

    def __prepareSelectedStoryPoint(self):
        storyPoints = self.lsStoryPointCtrl.storyPoints
        if not self.lsStoryPointCtrl.isStoryPointReceived(self.lsStoryPointCtrl.selectedStoryPointID):
            self.lsStoryPointCtrl.selectedStoryPointID = None
        if self.lsStoryPointCtrl.selectedStoryPointID is None:
            for storyPointID in storyPoints[::-1]:
                if self.lsStoryPointCtrl.isStoryPointReceived(storyPointID):
                    currentStoryPointID = storyPointID
                    break
            else:
                currentStoryPointID = storyPoints[0] if storyPoints else None

            self.__currentSlideIndex = self.lsStoryPointCtrl.getIndex(currentStoryPointID) if currentStoryPointID is not None else self.lsStoryPointCtrl.FIRST_STORY_POINT_INDEX
        else:
            self.__currentSlideIndex = self.lsStoryPointCtrl.getIndex(self.lsStoryPointCtrl.selectedStoryPointID)
        return

    def __updateButtonLock(self, tx):
        nexStoryPointID = self.lsStoryPointCtrl.getStoryPointIDByIndex(self.__currentSlideIndex + 1)
        if nexStoryPointID is None:
            return
        else:
            tx.setIsNextDisabled(not self.lsStoryPointCtrl.isStoryPointReceived(nexStoryPointID))
            return

    def __fillViewModel(self):
        with self.viewModel.transaction() as tx:
            isMuted = ls_account_settings.getSettings(AccountSettingsKeys.STORY_POINT_VOICEOVER_MUTED)
            tx.setIsVoiceoverActive(not isMuted)
            tx.setSlideNumber(self.__currentSlideIndex)
            self.__updateButtonLock(tx)
            if isMuted:
                playSound(META_VOICEOVER_MUTE)
            else:
                playSound(META_VOICEOVER_UNMUTE)
            playSound(META_STORY_POINT_OPEN_SOUND.format(self.__currentSlideIndex))

    def __onStoryPointStatusUpdated(self, token):
        self.lsStoryPointCtrl.selectedStoryPointID = token
        self.__prepareSelectedStoryPoint()
        self.__fillViewModel()


class NarrationWindow(LobbyNotificationWindow):

    def __init__(self, layoutID, parent=None):
        super(NarrationWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=NarrationView(layoutID), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
        self.__args = (layoutID,)

    def isParamsEqual(self, *args):
        return self.__args == args
