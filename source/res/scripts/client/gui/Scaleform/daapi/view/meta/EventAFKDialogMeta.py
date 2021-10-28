# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventAFKDialogMeta.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog

class EventAFKDialogMeta(SimpleDialog):

    def as_setDataS(self, imagePath):
        return self.flashObject.as_setData(imagePath) if self._isDAAPIInited() else None
