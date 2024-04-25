# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/pre_queue/ctx.py
from helpers import dependency
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HistoricalBattlesQueueCtx(QueueCtx):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, frontmanID, vehTypeCD):
        front = self.gameEventController.frontController.getSelectedFront()
        super(HistoricalBattlesQueueCtx, self).__init__(entityType=front.getFrontQueueType(), waitingID='prebattle/join')
        self._frontmanID = frontmanID
        self._vehTypeCD = vehTypeCD

    @property
    def frontmanID(self):
        return self._frontmanID

    @property
    def vehTypeCD(self):
        return self._vehTypeCD
