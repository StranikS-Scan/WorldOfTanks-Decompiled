# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_inject_widget_view.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class WTEventInjectWidget(InjectComponentAdaptor, IGlobalListener):
    __slots__ = ()

    def as_hideWidgetS(self):
        raise NotImplementedError

    def as_showWidgetS(self):
        raise NotImplementedError

    def onPrbEntitySwitched(self):
        if not self._isEventBattleSelected():
            self._hide()
        else:
            self._show()

    def _populate(self):
        super(WTEventInjectWidget, self)._populate()
        self.startGlobalListening()
        if not self._isEventBattleSelected():
            self._hide()
        else:
            self._show()

    def _isEventBattleSelected(self):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.EVENT_BATTLES) if self.prbDispatcher is not None else False

    def _show(self):
        self.as_showWidgetS()

    def _hide(self):
        self.as_hideWidgetS()

    def _dispose(self):
        self.stopGlobalListening()
        super(WTEventInjectWidget, self)._dispose()
