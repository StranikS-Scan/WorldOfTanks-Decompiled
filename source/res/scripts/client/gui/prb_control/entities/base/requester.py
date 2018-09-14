# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/requester.py


class IPrbListRequester(object):
    """
    Interface for prebattles list request.
    """

    def start(self, callback):
        """
        Starts to listen required events.
        Args:
            callback: routine that is invoked when list will be received/updated
        """
        pass

    def stop(self):
        """
        Stop to listen required events.
        """
        pass

    def request(self, ctx=None):
        """
        Send request to update list.
        Args:
            ctx: request context
        """
        pass


class IUnitRequestProcessor(object):

    def __init__(self):
        super(IUnitRequestProcessor, self).__init__()

    def init(self):
        pass

    def fini(self):
        pass

    def doRequest(self, ctx, methodName, *args, **kwargs):
        pass

    def doRequestChain(self, ctx, chain):
        pass

    def doRawRequest(self, methodName, *args, **kwargs):
        pass
