# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/BaseRallyView.py
from adisp import process
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.BaseRallyViewMeta import BaseRallyViewMeta
from gui.prb_control.entities.base.cooldown import getPrbRequestCoolDown
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.unit.listener import IUnitListener
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.MethodsRules import MethodsRules

class BaseRallyView(BaseRallyViewMeta, IUnitListener, MethodsRules):

    def __init__(self):
        super(BaseRallyView, self).__init__()

    def setData(self, initialData):
        LOG_DEBUG('BaseRallyView.setItemId stub implementation. Passed id is:', initialData)

    def getCoolDownRequests(self):
        return []

    @MethodsRules.delayable()
    def _populate(self):
        super(BaseRallyView, self)._populate()
        self._startListening()
        self._checkCoolDowns()

    def _dispose(self):
        self._stopListening()
        super(BaseRallyView, self)._dispose()

    def _handleSetPrebattleCoolDown(self, event):
        if event.requestID in self.getCoolDownRequests():
            self.as_setCoolDownS(event.coolDown, event.requestID)

    def _checkCoolDowns(self):
        for requestID in self.getCoolDownRequests():
            coolDown = getPrbRequestCoolDown(requestID)
            if coolDown > 0:
                self.as_setCoolDownS(coolDown, requestID)

    @process
    def _doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=isExit))

    @MethodsRules.delayable('_populate')
    def _startListening(self):
        """
        Start listening should be delayed until complete populate will be executed
        """
        self.startPrbListening()
        self.addListener(events.CoolDownEvent.PREBATTLE, self._handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def _stopListening(self):
        self.stopPrbListening()
        self.removeListener(events.CoolDownEvent.PREBATTLE, self._handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
