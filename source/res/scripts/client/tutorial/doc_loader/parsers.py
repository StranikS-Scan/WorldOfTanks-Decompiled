# Embedded file name: scripts/client/tutorial/doc_loader/parsers.py
import ResMgr
from helpers.html import translation
from items import _xml
from tutorial.data.descriptor import DescriptorData
from tutorial.data.chapter import Bonus, Chapter, Scene
from tutorial.doc_loader import sub_parsers
from tutorial.settings import GLOBAL_REFS_FILE_PATH, TUTORIAL_STOP_REASON_NAMES

class DescriptorParser(object):

    def __parseChapterSummaries(self, xmlCtx, section, descriptor):
        for _, subSection in _xml.getChildren(xmlCtx, section, 'chapters'):
            chapterID = _xml.readString(xmlCtx, subSection, 'chapter-id')
            title = translation(_xml.readString(xmlCtx, subSection, 'title'))
            descSec = _xml.getSubsection(xmlCtx, subSection, 'description')
            defDesc = translation(descSec.asString)
            abDesc = translation(descSec.readString('after-battle', defDesc))
            descriptions = (defDesc, abDesc)
            bonusSec = _xml.getSubsection(xmlCtx, subSection, 'bonus')
            bonus = Bonus(bonusSec.readInt('id', -1), bonusSec.readString('message'), sub_parsers._readBonusValues(bonusSec))
            forcedLoading = subSection.readInt('forced-loading', -1)
            pathSec = _xml.getSubsection(xmlCtx, subSection, 'file-path')
            defFilePath = pathSec.asString
            afterBattleFilePath = pathSec.readString('after-battle', defFilePath)
            filePaths = (defFilePath, afterBattleFilePath)
            sharedScene = subSection.readString('shared-scene')
            descriptor.addChapter(Chapter(chapterID, title, descriptions, bonus, forcedLoading, filePaths, sharedScene))

    def __parseStopBehavior(self, _, section, descriptor):
        subSection = section['behavior-if-stopping']
        if subSection:
            processing = subSection['items-revert'] or {}
            reasons = set()
            for _, subSection in processing.items():
                name = subSection.asString
                if name in TUTORIAL_STOP_REASON_NAMES:
                    reasons.add(TUTORIAL_STOP_REASON_NAMES[name])
                else:
                    raise Exception, 'Reason not found: {0:>s}'.format(name)

            if len(reasons):
                descriptor.setItemsRevertIfStop(reasons)

    def parse(self, filePath):
        descriptor = DescriptorData()
        section = ResMgr.openSection(filePath)
        if section is None:
            _xml.raiseWrongXml(None, filePath, 'can not open or read')
        xmlCtx = (None, filePath)
        descriptor.setGuiFilePath(_xml.readString(xmlCtx, section, 'gui'))
        descriptor.setInitialChapterID(_xml.readString(xmlCtx, section, 'initial-chapter'))
        self.__parseStopBehavior(xmlCtx, section, descriptor)
        self.__parseChapterSummaries(xmlCtx, section, descriptor)
        return descriptor


class ChapterParser(object):

    def __init__(self):
        super(ChapterParser, self).__init__()

    def __parseScene(self, xmlCtx, section, scene, flags, itemFlags, afterBattle = False, frontEffects = False):
        for _, subSec in _xml.getChildren(xmlCtx, section, 'gui-items'):
            item = sub_parsers._parseGuiItem(xmlCtx, subSec, flags, itemFlags)
            if item is not None:
                scene.addGuiItem(item)

        front = -1
        for _, subSec in _xml.getChildren(xmlCtx, section, 'post-effects'):
            effect = sub_parsers._parseEffect(xmlCtx, subSec, flags, afterBattle=afterBattle)
            if effect is not None:
                if frontEffects:
                    front += 1
                scene.addPostEffect(effect, front=front)

        front = -1
        for _, subSec in _xml.getChildren(xmlCtx, section, 'runtime-effects'):
            effect = sub_parsers._parseEffect(xmlCtx, subSec, flags, afterBattle=afterBattle)
            if effect is not None:
                if frontEffects:
                    front += 1
                scene.addEffect(effect, front=front)

        return

    def __parseSharedScene(self, chapter, scene, flags, itemFlags, afterBattle = False):
        filePath = chapter.getSharedScenePath()
        if filePath is None or not len(filePath):
            return
        else:
            section = ResMgr.openSection(filePath)
            if section is None:
                _xml.raiseWrongXml(None, filePath, 'can not open or read')
            xmlCtx = (None, filePath)
            self.__parseScene(xmlCtx, section, scene, flags, itemFlags, afterBattle=afterBattle, frontEffects=True)
            return

    def parse(self, chapter, afterBattle = False, initial = False):
        filePath = chapter.getFilePath(afterBattle=afterBattle)
        section = ResMgr.openSection(filePath)
        if section is None:
            _xml.raiseWrongXml(None, filePath, 'can not open or read')
        xmlCtx = (None, filePath)
        chapter.clear()
        flags = []
        itemFlags = []
        if 'initial-scene' in section.keys():
            chapter.setInitialSceneID(_xml.readString(xmlCtx, section, 'initial-scene'))
        if 'default-scene' in section.keys():
            chapter.setDefaultSceneID(_xml.readString(xmlCtx, section, 'default-scene'))
        for name, subSec in _xml.getChildren(xmlCtx, section, 'has-id'):
            entity = sub_parsers._parseEntity(xmlCtx, name, subSec, flags)
            if entity is not None:
                chapter.addHasIDEntity(entity)

        for _, subSec in _xml.getChildren(xmlCtx, section, 'triggers'):
            trigger = sub_parsers._parseTrigger(xmlCtx, subSec, flags, chapter)
            if trigger is not None:
                chapter.addTrigger(trigger)

        gVarIDs = []
        for name, subSec in _xml.getChildren(xmlCtx, section, 'vars'):
            if name == 'var-set':
                chapter.addVarSet(sub_parsers._parseVarSet(xmlCtx, subSec, flags))
            elif name == 'var-set-ref':
                gVarIDs.append(sub_parsers._parseID(xmlCtx, subSec, 'Specify a var ID'))
            else:
                _xml.raiseWrongXml(xmlCtx, name, 'Unknown tag')

        if len(gVarIDs):
            GlobalRefParser().parse(chapter, varIDs=gVarIDs, flags=flags)
        for _, sceneSec in _xml.getChildren(xmlCtx, section, 'scenes'):
            sceneID = sub_parsers._parseID(xmlCtx, sceneSec, 'Specify a unique name for the scene')
            scene = Scene(entityID=sceneID)
            self.__parseScene(xmlCtx, sceneSec, scene, flags, itemFlags, afterBattle=afterBattle)
            chapter.addScene(scene)

        if initial:
            scene = chapter.getInitialScene()
            self.__parseSharedScene(chapter, scene, flags, itemFlags)
        flags = filter(lambda flag: flag not in itemFlags, flags)
        chapter.setFlags(flags)
        chapter.setValid(True)
        return chapter


class GlobalRefParser(object):

    def __init__(self):
        super(GlobalRefParser, self).__init__()

    def parse(self, chapter, varIDs = None, flags = None):
        if varIDs is None:
            varIDs = []
        if flags is None:
            flags = []
        section = ResMgr.openSection(GLOBAL_REFS_FILE_PATH)
        if section is None:
            _xml.raiseWrongXml(None, GLOBAL_REFS_FILE_PATH, 'can not open or read')
        xmlCtx = (None, GLOBAL_REFS_FILE_PATH)
        if len(varIDs):
            for _, subSec in _xml.getChildren(xmlCtx, section, 'vars'):
                varID = sub_parsers._parseID(xmlCtx, subSec, 'Specify a var ID')
                if varID in varIDs:
                    chapter.addVarSet(sub_parsers._parseVarSet(xmlCtx, subSec, flags))

        return
