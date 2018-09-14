# Embedded file name: scripts/client/tutorial/doc_loader/parsers/__init__.py
import ResMgr
from helpers.html import translation
from items import _xml
from tutorial.data.chapter import Bonus, Chapter, Scene
from tutorial.data.descriptor import DescriptorData
from tutorial.data.hints import HintsData
from tutorial.doc_loader import sub_parsers
from tutorial.settings import TUTORIAL_STOP_REASON_NAMES, GLOBAL_REFS_FILE_PATH, BONUSES_REFS_FILE_PATH

class DescriptorParser(object):

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

    def __parseChapterSummaries(self, xmlCtx, section, descriptor):
        bonuses = BonusRefParser().parse()
        for _, subSection in _xml.getChildren(xmlCtx, section, 'chapters'):
            self._parseChapter(bonuses, descriptor, subSection, xmlCtx)

    def _parseChapter(self, bonuses, descriptor, subSection, xmlCtx):
        descriptor.addChapter(Chapter(*self._getCommonChapterValues(bonuses, subSection, xmlCtx)))

    def _getCommonChapterValues(self, bonuses, subSection, xmlCtx):
        chapterID = _xml.readString(xmlCtx, subSection, 'chapter-id')
        title = translation(_xml.readString(xmlCtx, subSection, 'title'))
        descSec = _xml.getSubsection(xmlCtx, subSection, 'description')
        defDesc = translation(descSec.asString)
        abDesc = translation(descSec.readString('after-battle', defDesc))
        descriptions = (defDesc, abDesc)
        bonus = self._parseBonus(xmlCtx, subSection, bonuses)
        forcedLoading = subSection.readInt('forced-loading', -1)
        pathSec = _xml.getSubsection(xmlCtx, subSection, 'file-path')
        defFilePath = pathSec.asString
        afterBattleFilePath = pathSec.readString('after-battle', defFilePath)
        filePaths = (defFilePath, afterBattleFilePath)
        sharedScene = subSection.readString('shared-scene')
        predefinedVars = []
        varsSection = subSection['vars'] or {}
        for name, varSection in varsSection.items():
            if name == 'var-set':
                predefinedVars.append(sub_parsers.parseVarSet(xmlCtx, varSection, ()))
            else:
                _xml.raiseWrongXml(xmlCtx, name, 'Unknown tag')

        return (chapterID,
         title,
         descriptions,
         bonus,
         forcedLoading,
         filePaths,
         sharedScene,
         predefinedVars)

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

    def _parseBonus(self, xmlCtx, section, bonuses):
        tags = section.keys()
        if 'bonus' in tags:
            subSection = section['bonus']
            return Bonus(subSection.readInt('id', -1), subSection.readString('message'), sub_parsers.readValues(subSection))
        if 'bonus-ref' in tags:
            bonusID = sub_parsers.parseID(xmlCtx, section['bonus-ref'], 'Specify a bonus ID')
            if bonusID in bonuses:
                return bonuses[bonusID]
            _xml.raiseWrongXml(xmlCtx, section.name, 'Bonus reference {0} is not found'.format(bonusID))
        else:
            _xml.raiseWrongXml(xmlCtx, section.name, 'Bonuses is not found')


class ChapterParser(object):

    def __init__(self):
        super(ChapterParser, self).__init__()

    def _parseScene(self, xmlCtx, section, scene, flags, itemFlags, afterBattle = False, frontEffects = False):
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

    def _parseSharedScene(self, chapter, scene, flags, itemFlags, afterBattle = False):
        filePath = chapter.getSharedScenePath()
        if filePath is None or not len(filePath):
            return
        else:
            section = ResMgr.openSection(filePath)
            if section is None:
                _xml.raiseWrongXml(None, filePath, 'can not open or read')
            xmlCtx = (None, filePath)
            self._parseScene(xmlCtx, section, scene, flags, itemFlags, afterBattle=afterBattle, frontEffects=True)
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
        self._parseEntities(xmlCtx, section, flags, chapter)
        self._parseTriggers(xmlCtx, section, flags, chapter)
        self._parseVars(xmlCtx, section, flags, chapter)
        self._parseScenes(xmlCtx, section, chapter, flags, itemFlags, afterBattle, initial)
        flags = filter(lambda flag: flag not in itemFlags, flags)
        chapter.setFlags(flags)
        chapter.setValid(True)
        return chapter

    def _parseVars(self, xmlCtx, section, flags, chapter):
        gVarIDs = []
        for name, subSec in _xml.getChildren(xmlCtx, section, 'vars'):
            if name == 'var-set':
                chapter.addVarSet(sub_parsers.parseVarSet(xmlCtx, subSec, flags))
            elif name == 'var-set-ref':
                gVarIDs.append(sub_parsers.parseID(xmlCtx, subSec, 'Specify a var ID'))
            else:
                _xml.raiseWrongXml(xmlCtx, name, 'Unknown tag')

        if gVarIDs:
            GlobalRefParser().parse(chapter, varIDs=gVarIDs, flags=flags)

    def _parseScenes(self, xmlCtx, section, chapter, flags, itemFlags, afterBattle, initial):
        for _, sceneSec in _xml.getChildren(xmlCtx, section, 'scenes'):
            sceneID = sub_parsers.parseID(xmlCtx, sceneSec, 'Specify a unique name for the scene')
            scene = Scene(entityID=sceneID)
            self._parseScene(xmlCtx, sceneSec, scene, flags, itemFlags, afterBattle=afterBattle)
            chapter.addScene(scene)

        if initial:
            scene = chapter.getInitialScene()
            self._parseSharedScene(chapter, scene, flags, itemFlags)

    def _parseTriggers(self, xmlCtx, section, flags, chapter):
        for _, subSec in _xml.getChildren(xmlCtx, section, 'triggers'):
            trigger = sub_parsers.parseTrigger(xmlCtx, subSec, flags, chapter)
            if trigger is not None:
                chapter.addTrigger(trigger)

        return

    def _parseEntities(self, xmlCtx, section, flags, chapter):
        for name, subSec in _xml.getChildren(xmlCtx, section, 'has-id'):
            entity = sub_parsers.parseEntity(xmlCtx, name, subSec, flags)
            if entity is not None:
                chapter.addHasIDEntity(entity)

        return


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
                varID = sub_parsers.parseID(xmlCtx, subSec, 'Specify a var ID')
                if varID in varIDs:
                    chapter.addVarSet(sub_parsers.parseVarSet(xmlCtx, subSec, flags))

        return


class BonusRefParser(object):

    def __init__(self):
        super(BonusRefParser, self).__init__()

    def parse(self):
        section = ResMgr.openSection(BONUSES_REFS_FILE_PATH)
        if section is None:
            _xml.raiseWrongXml(None, BONUSES_REFS_FILE_PATH, 'can not open or read')
        xmlCtx = (None, BONUSES_REFS_FILE_PATH)
        result = {}
        for _, subSec in _xml.getChildren(xmlCtx, section, 'bonuses'):
            bonusID = sub_parsers.parseID(xmlCtx, subSec, 'Specify a bonus ID')
            result[bonusID] = Bonus(subSec.readInt('id', -1), subSec.readString('message'), sub_parsers.readValues(subSec))

        return result


class HintsParser(object):

    @staticmethod
    def parse(filePath, excludedHints):
        hints = HintsData()
        section = ResMgr.openSection(filePath)
        if section is None:
            _xml.raiseWrongXml(None, filePath, 'can not open or read')
        xmlCtx = (None, filePath)
        hints.setGuiFilePath(_xml.readString(xmlCtx, section, 'gui'))
        for _, subSec in _xml.getChildren(xmlCtx, section, 'hints'):
            hint = sub_parsers.parseHint(xmlCtx, subSec)
            if hint['hintID'] not in excludedHints:
                hints.addHint(hint)

        return hints
