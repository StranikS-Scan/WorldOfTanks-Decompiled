# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportRespawnsViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CyberSportRespawnsViewMeta(DAAPIModule):

    def onReadyClick(self, userID):
        self._printOverrideError('onReadyClick')

    def as_setMapBGS(self, imgsource):
        if self._isDAAPIInited():
            return self.flashObject.as_setMapBG(imgsource)

    def as_setProgressS(self, time):
        if self._isDAAPIInited():
            return self.flashObject.as_setProgress(time)
