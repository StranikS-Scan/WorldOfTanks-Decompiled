# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntroMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyIntroView import BaseRallyIntroView

class FortIntroMeta(BaseRallyIntroView):

    def as_setIntroDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setIntroData(data)
