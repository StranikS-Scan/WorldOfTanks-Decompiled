# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/requester.py


class IPrbListRequester(object):

    def start(self, callback):
        pass

    def stop(self):
        pass

    def request(self, ctx=None):
        pass


class IUnitRequestProcessor(object):

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
