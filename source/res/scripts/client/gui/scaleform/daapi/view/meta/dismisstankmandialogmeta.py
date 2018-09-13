# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DismissTankmanDialogMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class DismissTankmanDialogMeta(DAAPIModule):

    def as_tankManS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_tankMan(value)
