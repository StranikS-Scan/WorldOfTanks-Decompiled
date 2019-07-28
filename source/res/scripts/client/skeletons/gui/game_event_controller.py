# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_event_controller.py


class IGameEventController(object):
    onProgressChanged = None
    onSelectedGeneralChanged = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def getGenerals(self):
        raise NotImplementedError

    def getGeneral(self, generalId):
        raise NotImplementedError

    def getGeneralsHistoryInfo(self):
        raise NotImplementedError

    def getSelectedGeneralID(self):
        raise NotImplementedError

    def getSelectedGeneral(self):
        raise NotImplementedError

    def setSelectedGeneralID(self, value):
        raise NotImplementedError

    def getEnergy(self):
        raise NotImplementedError

    def getFronts(self):
        raise NotImplementedError

    def getFront(self, frontID):
        raise NotImplementedError

    def getAvailableGeneralIDs(self):
        raise NotImplementedError

    def getBattleResultsInfo(self):
        raise NotImplementedError
