# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/fullscreen_event_view.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.fullscreen_event_view_model import FullscreenEventViewModel
from gui.impl.lobby.pet_system.event_view import PetEvent
from gui.impl.pub import WindowImpl
from frameworks.wulf import WindowFlags

class FullscreenEventView(PetEvent):
    LAYOUT_ID = R.views.mono.pet_system.fullscreen_event_view()

    def __init__(self, ctx):
        super(FullscreenEventView, self).__init__(FullscreenEventViewModel, ctx)

    @property
    def viewModel(self):
        return super(FullscreenEventView, self).getViewModel()

    def _updateData(self):
        with self.getViewModel().transaction() as tx:
            eventID = self._ctx.get('eventID')
            tx.setEventId(eventID)
            self._updateRewards()

    def _getEvents(self):
        events = super(FullscreenEventView, self)._getEvents()
        return events + ((self.viewModel.onClose, self._onClose),)


class FullscreenEventViewWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(FullscreenEventViewWindow, self).__init__(content=FullscreenEventView(**kwargs), wndFlags=WindowFlags.WINDOW_FULLSCREEN, layer=layer)
