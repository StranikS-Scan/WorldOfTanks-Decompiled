# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/data/bootcamp/chapter.py
from tutorial.data.chapter import Chapter

class BootcampLobbyChapter(Chapter):

    def __init__(self, sharedTriggers, sharedVars, *args, **kwargs):
        super(BootcampLobbyChapter, self).__init__(*args, **kwargs)
        self.__sharedTriggersPath = sharedTriggers
        self.__sharedVarsPath = sharedVars

    def getSharedTriggersPath(self):
        return self.__sharedTriggersPath

    def getSharedVarsPath(self):
        return self.__sharedVarsPath
