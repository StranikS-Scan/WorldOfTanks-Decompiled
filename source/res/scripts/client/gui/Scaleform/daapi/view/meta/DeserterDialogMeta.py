# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DeserterDialogMeta.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog

class DeserterDialogMeta(SimpleDialog):

    def as_setDataS(self, path, messageYOffset):
        return self.flashObject.as_setData(path, messageYOffset) if self._isDAAPIInited() else None
