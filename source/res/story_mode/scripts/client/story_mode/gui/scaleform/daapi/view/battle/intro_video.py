# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/intro_video.py
import BattleReplay
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.game_loading import loading
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.scaleform.daapi.view.common.base_video import BaseVideo
from story_mode.gui.scaleform.daapi.view.model.video_settings_model import getIntroVideoSettings
from story_mode.gui.shared.event_dispatcher import showPrebattleWindow
from story_mode.uilogging.story_mode.loggers import IntroVideoLogger

class IntroVideo(BaseVideo, IArenaLoadController):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def spaceLoadCompleted(self):
        loading.getLoader().idle()
        if BattleReplay.isPlaying():
            self._storyModeCtrl.goToBattle()
            self.destroy()
        else:
            self.as_loadedS()

    @UseStoryModeFading(hide=False)
    def onVideoComplete(self):
        super(IntroVideo, self).onVideoComplete()
        showPrebattleWindow(self._missionId)

    def _populate(self):
        super(IntroVideo, self)._populate()
        self._sessionProvider.addArenaCtrl(self)

    def _dispose(self):
        self._sessionProvider.removeArenaCtrl(self)
        super(IntroVideo, self)._dispose()

    def _getSettings(self):
        return getIntroVideoSettings()

    def _getLogger(self):
        return IntroVideoLogger()
