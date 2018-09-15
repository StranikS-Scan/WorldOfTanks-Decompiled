# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCIntroFadeOutMeta.py
from gui.Scaleform.framework.entities.View import View

class BCIntroFadeOutMeta(View):

    def finished(self):
        self._printOverrideError('finished')

    def as_startFadeoutS(self, animationTime):
        return self.flashObject.as_startFadeout(animationTime) if self._isDAAPIInited() else None
