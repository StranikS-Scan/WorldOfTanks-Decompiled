# Embedded file name: scripts/client/tutorial/doc_loader/__init__.py
import ResMgr
from tutorial.doc_loader.parsers import DescriptorParser, ChapterParser
from tutorial.settings import GLOBAL_REFS_FILE_PATH
from tutorial.logger import LOG_CURRENT_EXCEPTION

def loadDescriptorData(filePath, exParsers = None, clearCache = False):
    try:
        if exParsers is not None:
            imported = __import__(exParsers, globals(), locals(), ['init'])
            getattr(imported, 'init')()
        if clearCache:
            ResMgr.purge(filePath)
        return DescriptorParser().parse(filePath)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return

    return


def loadChapterData(chapter, afterBattle = False, initial = False):
    if chapter is not None and not chapter.isValid():
        try:
            ChapterParser().parse(chapter, afterBattle=afterBattle, initial=initial)
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
