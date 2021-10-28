# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventDifficultyViewMeta.py
from gui.Scaleform.framework.entities.View import View

class EventDifficultyViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def selectDifficulty(self, idx):
        self._printOverrideError('selectDifficulty')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setProgressS(self, value, condition, level):
        return self.flashObject.as_setProgress(value, condition, level) if self._isDAAPIInited() else None
