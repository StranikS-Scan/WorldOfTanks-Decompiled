# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IntroPageMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class IntroPageMeta(DAAPIModule):

    def stopVideo(self):
        self._printOverrideError('stopVideo')

    def handleError(self, data):
        self._printOverrideError('handleError')

    def as_playVideoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_playVideo(data)
