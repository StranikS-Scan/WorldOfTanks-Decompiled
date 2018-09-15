# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/ctx.py
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('__queueType', 'queueType'), ('getWaitingID', 'waitingID'))
class ChangeEventQueueTypeCtx(UnitRequestCtx):
    __slots__ = ('__queueType',)

    def __init__(self, queueType, waitingID=''):
        super(ChangeEventQueueTypeCtx, self).__init__(waitingID=waitingID)
        self.__queueType = queueType

    def getBattleType(self):
        return self.__queueType

    def getRequestType(self):
        return REQUEST_TYPE.CHANGE_EVENT_QUEUE_TYPE

    def getCooldown(self):
        pass
