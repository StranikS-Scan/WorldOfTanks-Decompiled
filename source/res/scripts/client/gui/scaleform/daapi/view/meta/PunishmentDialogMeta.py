# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PunishmentDialogMeta.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog

class PunishmentDialogMeta(SimpleDialog):

    def as_setMsgTitleS(self, value):
        return self.flashObject.as_setMsgTitle(value) if self._isDAAPIInited() else None
