# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/doc_loader/__init__.py
import ResMgr
from tutorial import settings
from tutorial.doc_loader import gui_config
from tutorial.doc_loader.parsers import DescriptorParser, ChapterParser
from tutorial.logger import LOG_CURRENT_EXCEPTION

def loadDescriptorData(setting, exParsers=None, clearCache=False):
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


def loadChapterData(chapter, chapterParser, initial=False):
    if chapter is not None and not chapter.isValid():
        try:
            parser = settings.createTutorialElement(chapterParser)
            parser.parse(chapter, initial=initial)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return

    return chapter


def clearChapterData(chapter):
    filePath = chapter.getFilePath()
    ResMgr.purge(filePath)
    chapter.clear()
