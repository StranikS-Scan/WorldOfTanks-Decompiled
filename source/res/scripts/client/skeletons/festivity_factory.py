# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/festivity_factory.py


class IFestivityFactory(object):

    def getRequester(self):
        raise NotImplementedError

    def getProcessor(self):
        raise NotImplementedError

    def getController(self):
        raise NotImplementedError
