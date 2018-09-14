# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WGNCDialogMeta.py
from gui.Scaleform.daapi.view.meta.SimpleDialogMeta import SimpleDialogMeta

class WGNCDialogMeta(SimpleDialogMeta):

    def doAction(self, actionId, isButtonClicked):
        self._printOverrideError('doAction')
