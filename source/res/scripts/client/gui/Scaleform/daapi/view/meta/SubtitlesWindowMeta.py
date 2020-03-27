# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SubtitlesWindowMeta.py
from gui.Scaleform.framework.entities.View import View

class SubtitlesWindowMeta(View):

    def as_showSubtitleS(self, text):
        return self.flashObject.as_showSubtitle(text) if self._isDAAPIInited() else None

    def as_hideSubtitleS(self):
        return self.flashObject.as_hideSubtitle() if self._isDAAPIInited() else None
