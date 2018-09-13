# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortClanListWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortClanListWindowMeta(DAAPIModule):

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
