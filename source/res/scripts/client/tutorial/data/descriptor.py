# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/data/descriptor.py


class DescriptorData(object):

    def __init__(self):
        super(DescriptorData, self).__init__()
        self.__guiFilePath = ''
        self.__contents = []
        self.__idMapping = {}
        self.__initialChapterID = ''

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

    def isChapterInitial(self, chapter, completed):
        result = False
        if chapter is not None:
            if chapter.getID() == self.__initialChapterID:
                result = True
            if not result:
                result = chapter.ignoreBonus(completed) or not chapter.isBonusReceived(completed)
        return result

    def getInitialChapterID(self, completed=None):
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
