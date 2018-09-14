# Embedded file name: scripts/client/tutorial/data/descriptor.py
from tutorial.data.chapter import ChapterProgress
from tutorial.settings import TUTORIAL_STOP_REASON_NAMES

class DescriptorData(object):

    def __init__(self):
        super(DescriptorData, self).__init__()
        self.__guiFilePath = ''
        self.__contents = []
        self.__idMapping = {}
        self.__initialChapterID = ''
        self.__itemsRevertSR = set(TUTORIAL_STOP_REASON_NAMES.values())

    def __iter__(self):
        return iter(self.__contents)

    def getGuiFilePath(self):
        return self.__guiFilePath

    def setGuiFilePath(self, filePath):
        self.__guiFilePath = filePath

    def setInitialChapterID(self, chapterID):
        self.__initialChapterID = chapterID

    def addChapter(self, chapter):
        self.__idMapping[chapter.getID()] = len(self.__contents)
        self.__contents.append(chapter)

    def getChapter(self, chapterID):
        result = None
        if chapterID in self.__idMapping:
            result = self.__contents[self.__idMapping[chapterID]]
        return result

    def getChapterIdx(self, chapterID):
        if chapterID in self.__idMapping.keys():
            return self.__idMapping[chapterID]
        else:
            return -1

    def getNumberOfChapters(self):
        return len(self.__contents)

    def isChapterInitial(self, chapter, completed):
        result = False
        if chapter is not None:
            if chapter.getID() == self.__initialChapterID:
                result = True
            if not result:
                result = chapter.ignoreBonus(completed) or not chapter.isBonusReceived(completed)
        return result

    def getInitialChapterID(self, completed = None):
        result = None
        if self.__initialChapterID:
            index = self.__idMapping.get(self.__initialChapterID, -1)
            if -1 < index < len(self.__contents):
                result = self.__contents[index].getID()
        if result is None:
            if completed is None:
                if self.__contents:
                    result = self.__contents[0].getID()
            else:
                result = self.getNextChapterID(completed)
        return result

    def getNextChapterID(self, completed):
        result = None
        for chapter in self.__contents:
            if chapter.hasBonus() and not chapter.isBonusReceived(completed):
                result = chapter.getID()
                break

        return result

    def getAllBonuses(self):
        result = 0
        for chapter in self.__contents:
            if chapter.hasBonus():
                result |= 1 << chapter.getBonusID()

        return result

    def areAllBonusesReceived(self, completed):
        result = True
        for chapter in self.__contents:
            if chapter.hasBonus() and not chapter.isBonusReceived(completed):
                result = False
                break

        return result

    def hasReceivedBonuses(self, completed, minimum = 1):
        if not completed:
            return False
        result = False
        counter = 0
        for chapter in self.__contents:
            if chapter.hasBonus() and chapter.isBonusReceived(completed):
                counter += 1
                if counter is minimum:
                    result = True
                    break

        return result

    def getProgress(self, completed, failed = -1):
        result = 0
        offset = 0
        for chapter in self.__contents:
            if chapter.hasBonus():
                if chapter.isBonusReceived(completed):
                    bit = ChapterProgress.PROGRESS_FLAG_COMPLETED
                elif failed is not -1 and chapter.isBonusReceived(failed):
                    bit = ChapterProgress.PROGRESS_FLAG_FAILED
                else:
                    bit = ChapterProgress.PROGRESS_FLAG_UNDEFINED
            else:
                bit = ChapterProgress.PROGRESS_FLAG_UNDEFINED
            result |= bit << offset
            offset += 2

        return result

    def setItemsRevertIfStop(self, reasons):
        self.__itemsRevertSR = reasons

    def isItemsRevertIfStop(self, reason):
        return reason in self.__itemsRevertSR

    def getChapterByIdx(self, idx):
        if idx < len(self.__contents):
            return self.__contents[idx]
        else:
            return None
