# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/data/quest.py
from gui.server_events.events_helpers import MISSIONS_STATES
from tutorial.data.has_id import HasID
from tutorial.data.chapter import Chapter

class QuestChapter(Chapter):

    def __init__(self, questConditions, image, unlockChapter, progressCondition, sharedTriggers, sharedEntities, sharedVars, isHidden, entityID, title, descriptions, bonus, forcedLoading, filePaths, sharedScene, predefinedVars):
        super(QuestChapter, self).__init__(entityID, title, descriptions, bonus, forcedLoading, filePaths, sharedScene, predefinedVars)
        self.__image = image
        self.__progressCondition = progressCondition
        self.__unlockChapter = unlockChapter
        self.__questConditions = questConditions
        self.__sharedTriggersPath = sharedTriggers
        self.__sharedEntitiesPath = sharedEntities
        self.__sharedVarsPath = sharedVars
        self.__isHidden = isHidden

    def getQuestConditions(self):
        return self.__questConditions

    def getSharedTriggersPath(self):
        return self.__sharedTriggersPath

    def getSharedEntitiesPath(self):
        return self.__sharedEntitiesPath

    def getSharedVarsPath(self):
        return self.__sharedVarsPath

    def getImage(self):
        return self.__image

    def getUnlockChapter(self):
        return self.__unlockChapter

    def getProgressCondition(self):
        return self.__progressCondition

    def isHidden(self):
        return self.__isHidden

    def getChapterStatus(self, descriptor, completed):
        unlockChapter = descriptor.getChapter(self.getUnlockChapter())
        if self.isHidden():
            return MISSIONS_STATES.NOT_AVAILABLE
        elif self.isBonusReceived(completed):
            return MISSIONS_STATES.COMPLETED
        else:
            return MISSIONS_STATES.NONE if unlockChapter is None or unlockChapter.isBonusReceived(completed) else MISSIONS_STATES.NOT_AVAILABLE


class ProgressCondition(HasID):

    def __init__(self, entityID, values):
        super(ProgressCondition, self).__init__(entityID=entityID)
        self.__values = values

    def getValues(self):
        return self.__values
