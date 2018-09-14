# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattlePageMeta.py
from gui.Scaleform.framework.entities.View import View

class BattlePageMeta(View):

    def openTestWindow(self):
        self._printOverrideError('openTestWindow')

    def as_checkDAAPIS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_checkDAAPI()
