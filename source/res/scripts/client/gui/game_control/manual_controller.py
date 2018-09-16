# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/manual_controller.py
import logging
from helpers import dependency
from skeletons.gui.game_control import IManualController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IBootcampController
from gui.doc_loaders import manual_xml_data_reader
_logger = logging.getLogger(__name__)

class ManualController(IManualController):
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(ManualController, self).__init__()
        self.__chapters = None
        return

    def getChaptersUIData(self):
        chaptersUIData = [ i['uiData'] for i in self.__getChapters() ]
        return chaptersUIData

    def getChapterUIData(self, chapterIndex):
        chapterFilename = None
        for chapter in self.__getChapters():
            if chapter['uiData']['index'] == chapterIndex:
                chapterFilename = chapter['filePath']

        currentChapter = manual_xml_data_reader.getChapterData(chapterFilename, self.__isBootcampEnabled(), self.getBootcampRunCount())
        return currentChapter

    def clear(self):
        self.__chapters = None
        return

    def isActivated(self):
        return self.lobbyContext.getServerSettings().isManualEnabled()

    def getBootcampRunCount(self):
        return self.bootcamp.runCount()

    def runBootcamp(self):
        _logger.debug('ManualChapterView. Requested bootcamp start.')
        self.bootcamp.runBootcamp()

    def __getChapters(self):
        if self.__chapters is None:
            self.__chapters = manual_xml_data_reader.getChapters(self.__isBootcampEnabled())
        return self.__chapters

    def __isBootcampEnabled(self):
        return self.lobbyContext.getServerSettings().isBootcampEnabled()
