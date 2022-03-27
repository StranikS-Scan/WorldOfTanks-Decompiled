# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/battle_replay.py


class IReplayConvertible(object):

    @staticmethod
    def dumpSafe(value):
        raise NotImplementedError

    @staticmethod
    def loadSafe(value):
        raise NotImplementedError
