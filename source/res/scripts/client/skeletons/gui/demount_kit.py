# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/demount_kit.py


class IDemountKitNovelty(object):
    onUpdated = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def showNovelty(self):
        raise NotImplementedError

    @property
    def noveltyCount(self):
        raise NotImplementedError

    def setAsSeen(self):
        raise NotImplementedError
