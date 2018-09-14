# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/IconDialog.py
from gui.Scaleform.daapi.view.meta.IconDialogMeta import IconDialogMeta

class IconDialog(IconDialogMeta):

    def __init__(self, meta, handler):
        super(IconDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self._meta = meta

    def _populate(self):
        super(IconDialog, self)._populate()
        self.as_setIconS(self._meta.getIcon())

    def _dispose(self):
        self._meta = None
        super(IconDialog, self)._dispose()
        return
