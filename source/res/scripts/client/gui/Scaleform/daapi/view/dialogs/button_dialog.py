# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/button_dialog.py
from SimpleDialog import SimpleDialog

class ButtonDialog(SimpleDialog):

    def _callHandler(self, buttonID):
        if self._handler is not None:
            self._handler(buttonID)
            self._isProcessed = True
        return
