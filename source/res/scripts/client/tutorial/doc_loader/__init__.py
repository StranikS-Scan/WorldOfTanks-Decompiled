# Embedded file name: scripts/client/tutorial/doc_loader/__init__.py
import ResMgr
from debug_utils import LOG_DEBUG
from tutorial import settings
from tutorial.doc_loader import gui_config
from tutorial.doc_loader.parsers import DescriptorParser, ChapterParser
from tutorial.settings import GLOBAL_REFS_FILE_PATH, TUTORIAL_SETTINGS
from tutorial.logger import LOG_CURRENT_EXCEPTION

def loadDescriptorData(setting, exParsers = None, clearCache = False):
    try:
        if exParsers is not None:
            imported = __import__(exParsers, globals(), locals(), ['init'])
            getattr(imported, 'init')()
        if clearCache:
            ResMgr.purge(setting.descriptorPath)
        classPath = setting.descriptorParser
        parser = settings.createTutorialElement(classPath)
        return parser.parse(setting.descriptorPath)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return

    return


def loadChapterData(chapter, chapterParser, afterBattle = False, initial = False):
    if chapter is not None and not chapter.isValid():
        try:
            parser = settings.createTutorialElement(chapterParser)
            parser.parse(chapter, afterBattle=afterBattle, initial=initial)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return

    return chapter


def clearChapterData(chapter):
    ResMgr.purge(GLOBAL_REFS_FILE_PATH)
    defPath = chapter.getFilePath(afterBattle=False)
    abPath = chapter.getFilePath(afterBattle=True)
    ResMgr.purge(defPath)
    if defPath != abPath:
        ResMgr.purge(abPath)
    chapter.clear()


def getQuestsDescriptor():
    global _questsDescriptor
    if _questsDescriptor is None:
        _questsDescriptor = loadDescriptorData(TUTORIAL_SETTINGS.QUESTS)
    return _questsDescriptor


_questsDescriptor = None
