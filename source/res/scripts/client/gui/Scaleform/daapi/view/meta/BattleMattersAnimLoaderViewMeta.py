# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleMattersAnimLoaderViewMeta.py
from gui.Scaleform.framework.entities.View import View

class BattleMattersAnimLoaderViewMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def as_setAnimationS(self, alias):
        return self.flashObject.as_setAnimation(alias) if self._isDAAPIInited() else None
