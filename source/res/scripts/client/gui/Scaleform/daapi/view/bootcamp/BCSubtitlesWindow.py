# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCSubtitlesWindow.py
from bootcamp.subtitles.subtitles import SubtitlesBase
from tutorial.gui.Scaleform.pop_ups import TutorialWindow
from gui.Scaleform.daapi.view.meta.SubtitlesWindowMeta import SubtitlesWindowMeta

class SubtitlesWindow(SubtitlesBase, SubtitlesWindowMeta, TutorialWindow):

    def onWindowClose(self):
        self._onMouseClicked('closeID')
        self._stop()

    def _asShowSubtitle(self, subtitle):
        self.as_showSubtitleS(subtitle)

    def _asHideSubtitle(self):
        self.as_hideSubtitleS()

    def _stop(self):
        self._content.clear()
        if self._tutorial is not None:
            for _, effect in self._gui.effects.iterEffects():
                if effect.isStillRunning(self.uniqueName):
                    effect.stop()

        self.destroy()
        return
