# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattleResultScreenMeta.py
from gui.Scaleform.framework.entities.View import View

class EventBattleResultScreenMeta(View):

    def closeView(self):
        self._printOverrideError('closeView')

    def as_setVictoryDataS(self, data):
        return self.flashObject.as_setVictoryData(data) if self._isDAAPIInited() else None

    def as_playAnimationS(self):
        return self.flashObject.as_playAnimation() if self._isDAAPIInited() else None
