# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/CyberSportDialog.py
from gui.Scaleform.daapi.view.dialogs.SimpleDialog import SimpleDialog
from gui.prb_control.prb_helpers import UnitListener

class CyberSportDialog(SimpleDialog, UnitListener):

    def __init__(self, meta, handler):
        super(CyberSportDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), handler, meta.getViewScopeType())

    def onUnitFunctionalFinished(self):
        self.destroy()

    def _populate(self):
        super(CyberSportDialog, self)._populate()

    def _dispose(self):
        super(CyberSportDialog, self)._dispose()
