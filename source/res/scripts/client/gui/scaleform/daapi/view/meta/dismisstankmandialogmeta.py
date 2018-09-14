# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DismissTankmanDialogMeta.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog

class DismissTankmanDialogMeta(SimpleDialog):

    def as_tankManS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_tankMan(value)
