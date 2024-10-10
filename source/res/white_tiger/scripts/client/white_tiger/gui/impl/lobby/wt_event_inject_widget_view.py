# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_inject_widget_view.py
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from white_tiger_common.wt_constants import QUEUE_TYPE

class WTEventInjectWidget(InjectComponentAdaptor, IGlobalListener):
    __slots__ = ()

    def as_hideWidgetS(self):
        pass

    def as_showWidgetS(self):
        pass

    def onPrbEntitySwitched(self):
        if not self._isEventBattleSelected():
            self.__hide()
        else:
            self.__show()

    def _populate(self):
        super(WTEventInjectWidget, self)._populate()
        self.startGlobalListening()
        self.__hide()

    def _isEventBattleSelected(self):
        return self.prbDispatcher.getFunctionalState().isQueueSelected(QUEUE_TYPE.WHITE_TIGER) if self.prbDispatcher is not None else False

    def __show(self):
        self.as_showWidgetS()

    def __hide(self):
        self.as_hideWidgetS()

    def _dispose(self):
        self.stopGlobalListening()
        super(WTEventInjectWidget, self)._dispose()
