# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SplashScreenMeta.py
from gui.Scaleform.daapi.view.meta.DAAPISimpleContainerMeta import DAAPISimpleContainerMeta

class SplashScreenMeta(DAAPISimpleContainerMeta):

    def onComplete(self):
        self._printOverrideError('onComplete')

    def onError(self):
        self._printOverrideError('onError')

    def fadeOutComplete(self):
        self._printOverrideError('fadeOutComplete')

    def as_playVideoS(self, data):
        return self.flashObject.as_playVideo(data) if self._isDAAPIInited() else None

    def as_setSizeS(self, width, height):
        return self.flashObject.as_setSize(width, height) if self._isDAAPIInited() else None

    def as_fadeOutS(self, time):
        return self.flashObject.as_fadeOut(time) if self._isDAAPIInited() else None
