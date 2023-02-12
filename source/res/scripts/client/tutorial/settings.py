# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/settings.py
from collections import namedtuple
from soft_exception import SoftException
TUTORIAL_VERSION = '0.4.0'
DOC_DIRECTORY = 'scripts/tutorial_docs'
BONUSES_REFS_FILE_PATH = '{0:>s}/bonuses-refs.xml'.format(DOC_DIRECTORY)

class INITIAL_FLAG(object):
    GUI_LOADED = 1
    CHAPTER_RESOLVED = 2
    INITIALIZED = GUI_LOADED | CHAPTER_RESOLVED


_SettingsDesc = namedtuple('_SettingsDesc', ('id', 'enabled', 'cacheEnabled', 'hintsEnabled', 'findChapterInCache', 'space', 'descriptorPath', 'descriptorParser', 'reqs', 'ctrl', 'gui', 'dispatcher', 'exParsers', 'chapterParser'))
_ClassPath = namedtuple('_ClassPath', ('module', 'clazz', 'args'))
TUTORIAL_LOBBY_DISPATCHER = _ClassPath('gui.Scaleform.lobby', 'SfLobbyDispatcher', ())
TUTORIAL_BATTLE_DISPATCHER = _ClassPath('tutorial.gui.Scaleform.battle_v2', 'SfBattleDispatcher', ())
TUTORIAL_DESCRIPTOR_PARSER = _ClassPath('tutorial.doc_loader.parsers', 'DescriptorParser', ())
TUTORIAL_CHAPTER_PARSER = _ClassPath('tutorial.doc_loader.parsers', 'ChapterParser', ())

class TUTORIAL_SETTINGS(object):
    SALES_TRIGGERS = _SettingsDesc('SALES_TRIGGERS', True, True, True, False, 'SALES_TRIGGERS', '{0:>s}/sales-descriptor.xml'.format(DOC_DIRECTORY), TUTORIAL_DESCRIPTOR_PARSER, _ClassPath('tutorial.control.sales.context', 'SalesStartReqs', ()), _ClassPath('tutorial.control.sales', 'SalesControlsFactory', ()), _ClassPath('gui.Scaleform.sales.proxy', 'SfSalesProxy', ()), TUTORIAL_LOBBY_DISPATCHER, 'tutorial.doc_loader.sub_parsers.sales', TUTORIAL_CHAPTER_PARSER)
    BOOTCAMP_LOBBY = _SettingsDesc('BOOTCAMP_LOBBY', True, False, False, False, 'BOOTCAMP_LOBBY', '{0:>s}/bootcamp-lobby-descriptor.xml'.format(DOC_DIRECTORY), _ClassPath('tutorial.doc_loader.parsers.bootcamp_lobby', 'BootcampLobbyDescriptorParser', ()), _ClassPath('tutorial.control.bootcamp.lobby.context', 'BootcampLobbyStartReqs', {}), _ClassPath('tutorial.control.bootcamp.lobby', 'BootcampLobbyControlsFactory', {}), _ClassPath('gui.Scaleform.bootcamp.lobby.proxy', 'SfBootcampLobbyProxy', {}), TUTORIAL_LOBBY_DISPATCHER, 'tutorial.doc_loader.sub_parsers.bootcamp_lobby', _ClassPath('tutorial.doc_loader.parsers.bootcamp_lobby', 'BootcampLobbyChapterParser', ()))
    SHORT_BOOTCAMP_LOBBY = _SettingsDesc('SHORT_BOOTCAMP_LOBBY', True, False, False, False, 'BOOTCAMP_LOBBY', '{0:>s}/short_bootcamp/short-bootcamp-lobby-descriptor.xml'.format(DOC_DIRECTORY), _ClassPath('tutorial.doc_loader.parsers.bootcamp_lobby', 'BootcampLobbyDescriptorParser', ()), _ClassPath('tutorial.control.bootcamp.lobby.context', 'BootcampLobbyStartReqs', {}), _ClassPath('tutorial.control.bootcamp.lobby', 'BootcampLobbyControlsFactory', {}), _ClassPath('gui.Scaleform.bootcamp.lobby.proxy', 'SfBootcampLobbyProxy', {}), TUTORIAL_LOBBY_DISPATCHER, 'tutorial.doc_loader.sub_parsers.bootcamp_lobby', _ClassPath('tutorial.doc_loader.parsers.bootcamp_lobby', 'BootcampLobbyChapterParser', ()))


class _SettingsCollection(dict):

    def init(self, clazz):
        self.clear()
        for name, settings in clazz.__dict__.iteritems():
            if name.startswith('_'):
                continue
            self[settings.id] = settings

    def getSettings(self, settingsID):
        settings = None
        return self[settingsID] if settingsID in self else settings


def createSettingsCollection():
    collection = _SettingsCollection()
    collection.init(TUTORIAL_SETTINGS)
    return collection


def createTutorialElement(classPath, init=None):
    imported = __import__(classPath.module, globals(), locals(), [classPath.clazz])
    if not imported:
        raise SoftException('Can not find class {0.module} in {0.clazz}'.format(classPath))
    clazz = getattr(imported, classPath.clazz)
    if init is None:
        init = classPath.args
    return clazz(*init)
