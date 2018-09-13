# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IconDialogMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class IconDialogMeta(DAAPIModule):

    def as_setIconS(self, path):
        if self._isDAAPIInited():
            return self.flashObject.as_setIcon(path)
