# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_1vs1_battles/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getWaitingID', 'waitingID'))
class RTS1x1BattleQueueCtx(QueueCtx):

    def __init__(self, waitingID=''):
        super(RTS1x1BattleQueueCtx, self).__init__(entityType=QUEUE_TYPE.RTS_1x1, waitingID=waitingID)
