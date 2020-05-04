# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/event_deserter_dialog.py
from gui.Scaleform.daapi.view.meta.EventDeserterDialogMeta import EventDeserterDialogMeta
from gui.impl import backport
from gui.impl.gen import R

class EventIngameDeserterDialog(EventDeserterDialogMeta):

    def _populate(self):
        super(EventIngameDeserterDialog, self)._populate()
        self.as_setHeaderS(backport.text(R.strings.event.postmortem_panel.has_locked_lives_message_title()))
