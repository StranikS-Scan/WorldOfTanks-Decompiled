# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/IconDialog.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog
from gui.Scaleform.daapi.view.meta.IconDialogMeta import IconDialogMeta

class IconDialog(IconDialogMeta, SimpleDialog):

    def __init__(self, meta, handler):
        SimpleDialog.__init__(self, meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        IconDialogMeta.__init__(self)
        self._meta = meta

    def _populate(self):
        super(IconDialog, self)._populate()
        self.as_setIconS(self._meta.getIcon())
