# Embedded file name: scripts/client/tutorial/doc_loader/parsers/quests.py
import ResMgr
from tutorial.data.quest import QuestChapter, ProgressCondition
from tutorial.doc_loader.parsers import DescriptorParser, ChapterParser
from items import _xml
from tutorial.data.chapter import Scene
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers.quests import readQuestConditions

class QuestsDescriptorParser(DescriptorParser):

    def _parseChapter(self, bonuses, descriptor, subSection, xmlCtx):
        sharedTriggers = subSection.readString('shared-triggers')
        sharedEntities = subSection.readString('shared-entities')
        sharedVars = subSection.readString('shared-vars')
        questConditions = readQuestConditions(subSection)
        image = subSection.readString('image')
        unlockChapter = subSection.readString('unlock-chapter')
        progressSec = _xml.getSubsection(xmlCtx, subSection, 'progress-condition')
        progressCondition = ProgressCondition(progressSec.readString('progressID'), sub_parsers.readValues(progressSec))
        isHidden = subSection.readBool('isHidden')
        descriptor.addChapter(QuestChapter(questConditions, image, unlockChapter, progressCondition, sharedTriggers, sharedEntities, sharedVars, isHidden, *self._getCommonChapterValues(bonuses, subSection, xmlCtx)))


class QuestsChapterParser(ChapterParser):

    def __init__(self):
        super(QuestsChapterParser, self).__init__()

    def parse(self, chapter, afterBattle = False, initial = False):
        chapter = super(QuestsChapterParser, self).parse(chapter, afterBattle, initial)
        self.__parseSharedTriggers(chapter)
        self.__parseSharedEntities(chapter)
        self.__parseSharedVars(chapter)
        return chapter

    def _parseScenes(self, xmlCtx, section, chapter, flags, itemFlags, afterBattle, initial):
        for _, sceneSec in _xml.getChildren(xmlCtx, section, 'scenes'):
            sceneID = sub_parsers.parseID(xmlCtx, sceneSec, 'Specify a unique name for the scene')
            scene = Scene(entityID=sceneID)
            self._parseScene(xmlCtx, sceneSec, scene, flags, itemFlags, afterBattle=afterBattle)
            self._parseSharedScene(chapter, scene, flags, itemFlags)
            chapter.addScene(scene)

    def __parseSharedTriggers(self, chapter):
        filePath = chapter.getSharedTriggersPath()
        if filePath is None or not len(filePath):
            return
        else:
            section = ResMgr.openSection(filePath)
            if section is None:
                _xml.raiseWrongXml(None, filePath, 'can not open or read')
            self._parseTriggers((None, filePath), section, [], chapter)
            return

    def __parseSharedEntities(self, chapter):
        filePath = chapter.getSharedEntitiesPath()
        if filePath is None or not len(filePath):
            return
        else:
            section = ResMgr.openSection(filePath)
            if section is None:
                _xml.raiseWrongXml(None, filePath, 'can not open or read')
            self._parseEntities((None, filePath), section, [], chapter)
            return

    def __parseSharedVars(self, chapter):
        filePath = chapter.getSharedVarsPath()
        if filePath is None or not len(filePath):
            return
        else:
            section = ResMgr.openSection(filePath)
            if section is None:
                _xml.raiseWrongXml(None, filePath, 'can not open or read')
            self._parseVars((None, filePath), section, [], chapter)
            return
