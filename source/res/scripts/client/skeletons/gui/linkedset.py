# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/linkedset.py


class ILinkedSetController(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isLinkedSetEnabled(self):
        raise NotImplementedError

    def isLinkedSetFinished(self):
        raise NotImplementedError

    def hasLinkedSetFinishToken(self):
        raise NotImplementedError

    def isFinalQuest(self, quest):
        raise NotImplementedError

    def getFinalQuest(self):
        raise NotImplementedError

    def getMaxMissionID(self):
        raise NotImplementedError

    def getCompletedButNotShowedQuests(self):
        raise NotImplementedError

    def getMissions(self):
        raise NotImplementedError

    def getMissionByID(self, missionID):
        raise NotImplementedError

    def isBootcampQuest(self, quest):
        raise NotImplementedError

    def getInitialMissionID(self):
        raise NotImplementedError

    def getBonusForBootcampMission(self):
        raise NotImplementedError

    def getCompletedLinkedSetQuests(self, filterFunc=None):
        raise NotImplementedError

    def getLinkedSetQuests(self, filterFunc=None):
        raise NotImplementedError
