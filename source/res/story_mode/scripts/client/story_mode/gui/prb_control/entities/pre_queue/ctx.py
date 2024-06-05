# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/prb_control/entities/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'))
class StoryModeQueueCtx(QueueCtx):

    def __init__(self, waitingID=''):
        super(StoryModeQueueCtx, self).__init__(entityType=QUEUE_TYPE.STORY_MODE, waitingID=waitingID)
