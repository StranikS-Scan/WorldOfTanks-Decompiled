# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/listener.py
from gui.prb_control.entities.base.listener import IPrbListener

class IPreQueueListener(IPrbListener):
    """
    Interface of prequeue listener.
    """

    def onEnqueued(self, queueType, *args):
        """
        Event that is called when player goes into queue.
        Args:
            queueType: joined queue type
        """
        pass

    def onDequeued(self, queueType, *args):
        """
        Event that is called when player leaves queue.
        Args:
            queueType: left queue type
        """
        pass

    def onEnqueueError(self, queueType, *args):
        """
        Event that is called when player receives enqueue error.
        Args:
            queueType: queue type that we're trying to join
        """
        pass

    def onKickedFromQueue(self, queueType, *args):
        """
        Event that is called when player was kicked from queue.
        Args:
            queueType: queue type that we're kicked from
        """
        pass

    def onKickedFromArena(self, queueType, *args):
        """
        Event that is called when player was kicked from arena.
        Args:
            queueType: queue type that we're kicked from
        """
        pass

    def onArenaJoinFailure(self, queueType, *args):
        """
        Event that is called when player was kicked during arena join.
        Args:
            queueType: queue type that we're kicked from
        """
        pass

    def onPreQueueSettingsChanged(self, diff):
        """
        Event that is called when player receives settings updates.
        Args:
            diff: settings changes
        """
        pass
