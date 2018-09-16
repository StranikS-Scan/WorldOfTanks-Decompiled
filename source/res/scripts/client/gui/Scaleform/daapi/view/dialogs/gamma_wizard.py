# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/gamma_wizard.py
from SimpleDialog import SimpleDialog

class GammaDialog(SimpleDialog):

    def __init__(self, meta, handler):
        super(GammaDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))

    def onTryClosing(self):
        return False
