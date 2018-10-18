# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/ingame_help.py
from gui.Scaleform.daapi.view.meta.EventHelpWindowMeta import EventHelpWindowMeta
from gui.Scaleform.locale.EVENT import EVENT
from gui.shared.events import IngameHelpWindowEvent

class EventIngameHelp(EventHelpWindowMeta):

    def _populate(self):
        self.fireEvent(IngameHelpWindowEvent(IngameHelpWindowEvent.POPULATE_WINDOW))
        super(EventIngameHelp, self)._populate()
        data = {'items': ({'descr': EVENT.LOADING_SCREEN_GAMEPLAY_TIPS_1}, {'descr': EVENT.LOADING_SCREEN_GAMEPLAY_TIPS_2}, {'descr': EVENT.LOADING_SCREEN_GAMEPLAY_TIPS_3})}
        self.as_setEventInfoPanelDataS(data)

    def _dispose(self):
        super(EventIngameHelp, self)._dispose()
        self.fireEvent(IngameHelpWindowEvent(IngameHelpWindowEvent.DISPOSE_WINDOW))
