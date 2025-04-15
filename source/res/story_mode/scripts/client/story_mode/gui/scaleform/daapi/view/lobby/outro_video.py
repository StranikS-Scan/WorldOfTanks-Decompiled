# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/lobby/outro_video.py
import typing
from story_mode.gui.scaleform.daapi.view.common.base_video import BaseVideo
from story_mode.gui.scaleform.daapi.view.model.video_settings_model import getOutroVideoSettings
from story_mode.uilogging.story_mode.loggers import OutroVideoLogger

class OutroVideo(BaseVideo):

    def __init__(self, ctx):
        super(OutroVideo, self).__init__(ctx)
        self._arenaUniqueID = ctx.get('arenaUniqueID')

    def onVideoComplete(self):
        super(OutroVideo, self).onVideoComplete()
        self._storyModeCtrl.onOutroVideoComplete(self._arenaUniqueID)

    def _populate(self):
        super(OutroVideo, self)._populate()
        self.as_loadedS()

    def _getSettings(self):
        return getOutroVideoSettings()

    def _getLogger(self):
        return OutroVideoLogger()

    def _getLoadingImage(self):
        pass
