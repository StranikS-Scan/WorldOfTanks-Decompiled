# Embedded file name: scripts/client/tutorial/settings.py
from collections import namedtuple
TUTORIAL_VERSION = '0.3.7'
DOC_DIRECTORY = 'scripts/tutorial_docs'
GLOBAL_REFS_FILE_PATH = '{0:>s}/global-refs.xml'.format(DOC_DIRECTORY)
BONUSES_REFS_FILE_PATH = '{0:>s}/bonuses-refs.xml'.format(DOC_DIRECTORY)
TUTORIAL_AVG_SESSION_TIME = 5

class PLAYER_XP_LEVEL(object):
    NEWBIE = 0
    NORMAL = 1


class TUTORIAL_STOP_REASON(object):
    PLAYER_ACTION = 1
    CRITICAL_ERROR = 2
    DISCONNECT = 3
    DEFAULT = PLAYER_ACTION


TUTORIAL_STOP_REASON_NAMES = dict([ (k, v) for k, v in TUTORIAL_STOP_REASON.__dict__.iteritems() if not k.startswith('_') ])
_SettingsDesc = namedtuple('_SettingsDesc', ('id', 'enabled', 'findChapterInCache', 'space', 'descriptorPath', 'descriptorParser', 'reqs', 'ctrl', 'gui', 'dispatcher', 'exParsers', 'chapterParser'))
_ClassPath = namedtuple('_ClassPath', ('module', 'clazz', 'args'))
TUTORIAL_LOBBY_DISPATCHER = _ClassPath('gui.Scaleform.lobby', 'SfLobbyDispatcher', ())
TUTORIAL_BATTLE_DISPATCHER = _ClassPath('gui.Scaleform.battle', 'SfBattleDispatcher', ())
TUTORIAL_DESCRIPTOR_PARSER = _ClassPath('tutorial.doc_loader.parsers', 'DescriptorParser', ())
TUTORIAL_CHAPTER_PARSER = _ClassPath('tutorial.doc_loader.parsers', 'ChapterParser', ())

class TUTORIAL_SETTINGS(object):
    BATTLE = _SettingsDesc('BATTLE', True, True, 'BATTLE', '{0:>s}/battle-descriptor.xml'.format(DOC_DIRECTORY), TUTORIAL_DESCRIPTOR_PARSER, _ClassPath('tutorial.control.battle.context', 'BattleStartReqs', ()), _ClassPath('tutorial.control.battle', 'BattleControlsFactory', ()), _ClassPath('gui.Scaleform.battle', 'BattleLayout', ('TutorialBattleLayout.swf',)), TUTORIAL_BATTLE_DISPATCHER, 'tutorial.doc_loader.sub_parsers.battle', TUTORIAL_CHAPTER_PARSER)
    OFFBATTLE = _SettingsDesc('OFFBATTLE', True, False, 'BATTLE', '{0:>s}/offbattle-descriptor.xml'.format(DOC_DIRECTORY), TUTORIAL_DESCRIPTOR_PARSER, _ClassPath('tutorial.control.offbattle.context', 'OffbattleStartReqs', ()), _ClassPath('tutorial.control.offbattle', 'OffbattleControlsFactory', ()), _ClassPath('gui.Scaleform.offbattle', 'SfOffbattleProxy', ()), TUTORIAL_LOBBY_DISPATCHER, 'tutorial.doc_loader.sub_parsers.offbattle', TUTORIAL_CHAPTER_PARSER)
    TRIGGERS_CHAINS = _SettingsDesc('TRIGGERS_CHAINS', True, False, 'TRIGGERS_CHAINS', '{0:>s}/chains-descriptor.xml'.format(DOC_DIRECTORY), TUTORIAL_DESCRIPTOR_PARSER, _ClassPath('tutorial.control.chains', 'ChainsStartReqs', ()), _ClassPath('tutorial.control.chains', 'ChainsControlsFactory', ()), _ClassPath('gui.Scaleform.chains', 'SfChainsProxy', ()), TUTORIAL_LOBBY_DISPATCHER, 'tutorial.doc_loader.sub_parsers.chains', TUTORIAL_CHAPTER_PARSER)
    QUESTS = _SettingsDesc('QUESTS', True, False, 'QUESTS', '{0:>s}/quests-descriptor.xml'.format(DOC_DIRECTORY), _ClassPath('tutorial.doc_loader.parsers.quests', 'QuestsDescriptorParser', ()), _ClassPath('tutorial.control.quests.context', 'QuestsStartReqs', ()), _ClassPath('tutorial.control.quests', 'QuestsControlsFactory', ()), _ClassPath('gui.Scaleform.quests', 'SfQuestsProxy', ()), TUTORIAL_LOBBY_DISPATCHER, 'tutorial.doc_loader.sub_parsers.quests', _ClassPath('tutorial.doc_loader.parsers.quests', 'QuestsChapterParser', ()))
    BATTLE_QUESTS = _SettingsDesc('BATTLE_QUESTS', True, False, 'BATTLE_QUESTS', '{0:>s}/battle-quests-descriptor.xml'.format(DOC_DIRECTORY), TUTORIAL_DESCRIPTOR_PARSER, _ClassPath('tutorial.control.quests.battle.context', 'BattleQuestsStartReqs', ()), _ClassPath('tutorial.control.quests.battle', 'BattleQuestsControlsFactory', ()), _ClassPath('gui.Scaleform.quests.battle.proxy', 'BattleQuestsProxy', ()), TUTORIAL_BATTLE_DISPATCHER, 'tutorial.doc_loader.sub_parsers.battle_quests', TUTORIAL_CHAPTER_PARSER)


class _SettingsCollection(dict):

    def init(self, clazz):
        self.clear()
        for name, settings in clazz.__dict__.iteritems():
            if name.startswith('_'):
                continue
            raise settings.id not in self or AssertionError('Settings ID must be unique')
            self[settings.id] = settings

    def getSettings(self, settingsID):
        settings = None
        if settingsID in self:
            return self[settingsID]
        else:
            return settings


def createSettingsCollection():
    collection = _SettingsCollection()
    collection.init(TUTORIAL_SETTINGS)
    return collection


def createTutorialElement(classPath, init = None):
    imported = __import__(classPath.module, globals(), locals(), [classPath.clazz])
    if not imported:
        raise ValueError('Can not find class {0.module} in {0.clazz}'.format(classPath))
    clazz = getattr(imported, classPath.clazz)
    if init is None:
        init = classPath.args
    return clazz(*init)
