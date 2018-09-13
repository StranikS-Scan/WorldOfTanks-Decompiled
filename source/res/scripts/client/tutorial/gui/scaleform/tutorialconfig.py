# Embedded file name: scripts/client/tutorial/gui/Scaleform/TutorialConfig.py
import ResMgr
from items import _xml
from tutorial.doc_loader import sub_parsers
from tutorial.gui.commands import CommandData

class TutorialConfig(object):

    def __init__(self):
        super(TutorialConfig, self).__init__()
        self.__sceneAliases = {}
        self.__sceneMethods = {}
        self.__guiItems = {}
        self.__commands = {}

    def __readSceneAliasesSection(self, xmlCtx, section):
        self.__sceneAliases.clear()
        self.__sceneMethods.clear()
        for tagName, subSection in _xml.getChildren(xmlCtx, section, 'scene-aliases'):
            sceneID = subSection.asString
            self.__sceneAliases[tagName] = sceneID
            self.__sceneMethods[sceneID] = _xml.readString(xmlCtx, subSection, 'go-to')

    def __readGuiItemsSection(self, xmlCtx, section):
        self.__guiItems.clear()
        for _, subSection in _xml.getChildren(xmlCtx, section, 'gui-items'):
            itemID = sub_parsers._parseID(xmlCtx, subSection, 'Specify a GUI item ID')
            path = _xml.readString(xmlCtx, subSection, 'path')
            self.__guiItems[itemID] = {'path': path,
             'locked': True}

    def __readCommandsSection(self, xmlCtx, section):
        self.__commands.clear()
        for _, subSection in _xml.getChildren(xmlCtx, section, 'gui-commands'):
            commandID = sub_parsers._parseID(xmlCtx, subSection, 'Specify a command ID')
            cmdType = _xml.readString(xmlCtx, subSection, 'type')
            command = _xml.readString(xmlCtx, subSection, 'name')
            argsSec = _xml.getChildren(xmlCtx, subSection, 'args')
            args = []
            for name, argSec in argsSec:
                args.append(sub_parsers._readVarValue(name, argSec))

            self.__commands[commandID] = CommandData(cmdType, command, args)

    def loadConfig(self, filePath):
        if not len(filePath):
            return
        else:
            section = ResMgr.openSection(filePath)
            if section is None:
                _xml.raiseWrongXml(None, filePath, 'can not open or read')
            xmlCtx = (None, filePath)
            self.__readSceneAliasesSection(xmlCtx, section)
            self.__readGuiItemsSection(xmlCtx, section)
            self.__readCommandsSection(xmlCtx, section)
            return

    def reloadConfig(self, filePath):
        if not len(filePath):
            return
        ResMgr.purge(filePath)
        self.loadConfig(filePath)

    def getSceneID(self, guiPage):
        try:
            return self.__sceneAliases[guiPage]
        except KeyError:
            return None

        return None

    def getGoToSceneMethod(self, sceneID):
        try:
            return self.__sceneMethods[sceneID]
        except KeyError:
            return None

        return None

    def getItem(self, targetID):
        if targetID in self.__guiItems:
            return self.__guiItems[targetID].copy()
        else:
            return {'path': '',
             'locked': False}

    def addItem(self, targetID, path, locked = False):
        self.__guiItems[targetID] = {'path': path,
         'locked': locked}

    def getCommand(self, commandID):
        try:
            return self.__commands[commandID]
        except KeyError:
            return None

        return None

    def removeItem(self, targetID):
        item = self.__guiItems.get(targetID)
        if item is not None and not item['locked']:
            self.__guiItems.pop(targetID)
        return
