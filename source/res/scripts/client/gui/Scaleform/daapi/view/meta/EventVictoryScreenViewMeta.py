# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventVictoryScreenViewMeta.py
from gui.Scaleform.framework.entities.View import View

class EventVictoryScreenViewMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def onVictoryScreenSound(self, id):
        self._printOverrideError('onVictoryScreenSound')

    def as_setVictoryDataS(self, data):
        return self.flashObject.as_setVictoryData(data) if self._isDAAPIInited() else None

    def as_setProgressDataS(self, data):
        return self.flashObject.as_setProgressData(data) if self._isDAAPIInited() else None

    def as_setProgressValueS(self, value, oldValue=-1):
        return self.flashObject.as_setProgressValue(value, oldValue) if self._isDAAPIInited() else None
