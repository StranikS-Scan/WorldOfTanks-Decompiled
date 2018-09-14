# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/SandboxQueueDialog.py
from gui import makeHtmlString
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import HideWindowEvent
from helpers import i18n
from gui.Scaleform.daapi.view.meta.PvESandboxQueueWindowMeta import PvESandboxQueueWindowMeta

class SandboxQueueDialog(PvESandboxQueueWindowMeta):

    def onWindowClose(self):
        self.cancel()

    def cancel(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.exitFromQueue()
        self.destroy()
        return

    def _populate(self):
        self.addListener(HideWindowEvent.HIDE_SANDBOX_QUEUE_DIALOG, self.__handleHideDialog, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SandboxQueueDialog, self)._populate()
        self.as_setDataS({'title': MENU.PVESANDBOX_QUEUE_TITLE,
         'message': MENU.PVESANDBOX_QUEUE_MESSAGE,
         'playerTimeTextStart': i18n.makeString(MENU.PVESANDBOX_QUEUE_PLAYER_WAITING_TIME) + makeHtmlString('html_templates:lobby/queue/sandbox', 'timeTextStart'),
         'playerTimeTextEnd': makeHtmlString('html_templates:lobby/queue/sandbox', 'timeTextEnd'),
         'updatePeriod': 1,
         'timePointcuts': {'firstPointcut': {},
                           'lastPointcut': {'value': 60,
                                            'text': i18n.makeString(MENU.PVESANDBOX_QUEUE_MORE_N_MINUTES, minutes=1)},
                           'betweenPointcutsTextAlias': MENU.PVESANDBOX_QUEUE_UNITS}})

    def _dispose(self):
        self.removeListener(HideWindowEvent.HIDE_SANDBOX_QUEUE_DIALOG, self.__handleHideDialog, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SandboxQueueDialog, self)._dispose()

    def __handleHideDialog(self, _):
        self.destroy()
