# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/leviathanPreview/LeviathanPreview.py
from gui.Scaleform.daapi.view.meta.LeviathanPreviewMeta import LeviathanPreviewMeta
from gui.shared import event_dispatcher, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi import LobbySubView

class LeviathanPreview(LobbySubView, LeviathanPreviewMeta):
    __background_alpha__ = 0.0

    def _populate(self):
        super(LeviathanPreview, self)._populate()
        self.fireEvent(events.LeviathanPreviewEvent(events.LeviathanPreviewEvent.LEVIATHAN_WINDOW_OPENED), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.fireEvent(events.LeviathanPreviewEvent(events.LeviathanPreviewEvent.LEVIATHAN_WINDOW_CLOSED), EVENT_BUS_SCOPE.LOBBY)
        super(LeviathanPreview, self)._dispose()

    def closeView(self):
        self.onBackClick()

    def onBackClick(self):
        event_dispatcher.showHangar()
