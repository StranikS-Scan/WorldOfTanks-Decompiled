# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCSecondaryHint.py
from gui.Scaleform.daapi.view.meta.BCSecondaryHintMeta import BCSecondaryHintMeta
from gui.shared import events, EVENT_BUS_SCOPE

class BCSecondaryHint(BCSecondaryHintMeta):

    def onSecondayHintShow(self, event):
        self.as_showHintS(event.eventArg)

    def onSecondayHintHide(self, event):
        self.as_hideHintS()

    def _populate(self):
        super(BCSecondaryHint, self)._populate()
        self.addListener(events.BootcampEvent.SHOW_SECONDARY_HINT, self.onSecondayHintShow, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.BootcampEvent.HIDE_SECONDARY_HINT, self.onSecondayHintHide, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.BootcampEvent.SHOW_SECONDARY_HINT, self.onSecondayHintShow, EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.BootcampEvent.HIDE_SECONDARY_HINT, self.onSecondayHintHide, EVENT_BUS_SCOPE.BATTLE)
        super(BCSecondaryHint, self)._dispose()
