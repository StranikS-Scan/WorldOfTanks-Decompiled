# Embedded file name: scripts/client/tutorial/settings.py
from collections import namedtuple
TUTORIAL_VERSION = '0.3.4'
DOC_DIRECTORY = 'scripts/tutorial_docs'
GLOBAL_REFS_FILE_PATH = '{0:>s}/global-refs.xml'.format(DOC_DIRECTORY)
TUTORIAL_AVG_SESSION_TIME = 5
_SettingsDesc = namedtuple('_SettingsDesc', ('id', 'enabled', 'findChapterInCache', 'space', 'descriptorPath', 'reqs', 'ctrl', 'gui', 'dispatcher', 'exParsers'))
_ClassPath = namedtuple('_ClassPath', ('module', 'clazz', 'args'))

class TUTORIAL_SETTINGS(object):
    DEFAULT_SETTINGS = 'OFFBATTLE'
    BATTLE = _SettingsDesc(1, True, True, 'BATTLE', '{0:>s}/battle-descriptor.xml'.format(DOC_DIRECTORY), _ClassPath('tutorial.control.battle.context', 'BattleStartReqs', tuple()), _ClassPath('tutorial.control.battle', 'BattleControlsFactory', tuple()), _ClassPath('gui.Scaleform.battle.layout', 'BattleLayout', ('TutorialBattleLayout.swf',)), _ClassPath('gui.Scaleform.battle.SfBattleDispatcher', 'SfBattleDispatcher', ({'visibleIfRun': False,
      'restartStatus': '',
      'refuseStatus': ''},)), 'tutorial.doc_loader.sub_parsers.battle')
    OFFBATTLE = _SettingsDesc(2, True, False, 'BATTLE', '{0:>s}/offbattle-descriptor.xml'.format(DOC_DIRECTORY), _ClassPath('tutorial.control.offbattle.context', 'OffbattleStartReqs', tuple()), _ClassPath('tutorial.control.offbattle', 'OffbattleControlsFactory', tuple()), _ClassPath('gui.Scaleform.offbattle', 'SfOffbattleProxy', tuple()), _ClassPath('gui.Scaleform.lobby', 'SfLobbyDispatcher', ({'visibleIfRun': False,
      'restartStatus': '#battle_tutorial:dispatcher/statuses/restart',
      'refuseStatus': '#battle_tutorial:dispatcher/statuses/refuse'},)), 'tutorial.doc_loader.sub_parsers.offbattle')

    @classmethod
    def getSettings(cls, name):
        return getattr(TUTORIAL_SETTINGS, name, TUTORIAL_SETTINGS.OFFBATTLE)

    @classmethod
    def getClass(cls, data):
        imported = __import__(data.module, globals(), locals(), [data.clazz])
        return getattr(imported, data.clazz)

    @classmethod
    def factory(cls, data, init = None):
        if init is None:
            init = data.args
        return cls.getClass(data)(*init)


class PLAYER_XP_LEVEL(object):
    NEWBIE = 0
    NORMAL = 1


class TUTORIAL_STOP_REASON(object):
    PLAYER_ACTION = 1
    CRITICAL_ERROR = 2
    DISCONNECT = 3
    DEFAULT = PLAYER_ACTION


TUTORIAL_STOP_REASON_NAMES = dict([ (k, v) for k, v in TUTORIAL_STOP_REASON.__dict__.iteritems() if not k.startswith('_') ])
