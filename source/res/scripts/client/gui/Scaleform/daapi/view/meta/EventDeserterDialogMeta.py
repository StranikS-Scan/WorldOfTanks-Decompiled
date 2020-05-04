# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventDeserterDialogMeta.py
from gui.Scaleform.daapi.view.dialogs.deserter_dialog import IngameDeserterDialog

class EventDeserterDialogMeta(IngameDeserterDialog):

    def as_setHeaderS(self, header):
        return self.flashObject.as_setHeader(header) if self._isDAAPIInited() else None
