# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/LegalInfoWindow.py
from gui.Scaleform.daapi.view.meta.LegalInfoWindowMeta import LegalInfoWindowMeta
from debug_utils import LOG_ERROR
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events

class LegalInfoWindow(LegalInfoWindowMeta):

    def __init__(self, ctx = None):
        super(LegalInfoWindow, self).__init__()

    def startListening(self):
        self.addListener(events.HideWindowEvent.HIDE_LEGAL_INFO_WINDOW, self.__handleLIWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def stopListening(self):
        self.removeListener(events.HideWindowEvent.HIDE_LEGAL_INFO_WINDOW, self.__handleLIWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def __handleLIWindowHide(self, _):
        self.destroy()

    def _populate(self):
        self.startListening()
        super(LegalInfoWindow, self)._populate()

    def _dispose(self):
        self.stopListening()
        super(LegalInfoWindow, self)._dispose()

    def getLegalInfo(self):
        info = ''
        LICENSES_PATH = 'licenses.txt'
        try:
            f = open(LICENSES_PATH, 'r')
        except IOError:
            LOG_ERROR('cannot open %s' % LICENSES_PATH)
        else:
            info = f.read()
            f.close()

        self.as_setLegalInfoS(info)

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()
