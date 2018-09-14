# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportRespawnsFormMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class CyberSportRespawnsFormMeta(BaseRallyRoomView):

    def onReadyClick(self, userID):
        self._printOverrideError('onReadyClick')

    def as_setMapBGS(self, imgsource):
        if self._isDAAPIInited():
            return self.flashObject.as_setMapBG(imgsource)

    def as_setProgressS(self, time):
        if self._isDAAPIInited():
            return self.flashObject.as_setProgress(time)
