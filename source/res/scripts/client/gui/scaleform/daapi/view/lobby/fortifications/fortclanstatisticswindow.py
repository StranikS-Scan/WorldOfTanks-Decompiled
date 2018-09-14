# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortClanStatisticsWindow.py
from gui.Scaleform.daapi.view.meta.FortClanStatisticsWindowMeta import FortClanStatisticsWindowMeta

class FortClanStatisticsWindow(FortClanStatisticsWindowMeta):

    def __init__(self, ctx = None):
        super(FortClanStatisticsWindow, self).__init__()
        self.data = ctx
        self.data.onDataChanged += self.onDataChanged

    def _populate(self):
        super(FortClanStatisticsWindow, self)._populate()
        self.as_setDataS(self.data.getData())

    def _dispose(self):
        self.data.stopFortListening()
        super(FortClanStatisticsWindow, self)._dispose()

    def onDataChanged(self):
        self.as_setDataS(self.data.getData())

    def onWindowClose(self):
        self.destroy()
