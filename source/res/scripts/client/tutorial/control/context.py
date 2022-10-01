# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/context.py
from abc import ABCMeta, abstractmethod
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IBootcampController
from tutorial.control import TutorialProxyHolder
from tutorial.logger import LOG_MEMORY, LOG_ERROR
import SoundGroups
import Event
__all__ = ('StartReqs', 'BonusesRequester', 'SoundPlayer', 'GlobalStorage')

class StartReqs(object):
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)

    def __del__(self):
        LOG_MEMORY('StartReqs deleted: {0:>s}'.format(self))

    def isEnabled(self):
        isBootcampTutorial = self._isBootcamp()
        isInBootcamp = self.bootcampController.isInBootcamp()
        if isBootcampTutorial:
            return isInBootcamp
        isTutorialEnabled = self.lobbyContext.getServerSettings().isTutorialEnabled()
        isBootcampEnabled = self.lobbyContext.getServerSettings().isBootcampEnabled()
        return isTutorialEnabled and not isBootcampEnabled and not isInBootcamp

    def prepare(self, ctx):
        raise NotImplementedError

    def process(self, descriptor, ctx):
        raise NotImplementedError

    def _isBootcamp(self):
        return False


class BonusesRequester(TutorialProxyHolder):
    __meta__ = ABCMeta

    def __init__(self, completed):
        super(BonusesRequester, self).__init__()
        self._completed = completed

    def getCompleted(self):
        return self._completed

    def setCompleted(self, completed):
        self._completed = completed

    def isStillRunning(self):
        return False

    def getChapter(self, chapterID=None):
        chapter = self._data
        if chapterID:
            chapter = self._descriptor.getChapter(chapterID)
        return chapter

    @abstractmethod
    def request(self, chapterID=None):
        pass


class SOUND_EVENT(object):
    TASK_FAILED = 0
    TASK_COMPLETED = 1
    NEXT_CHAPTER = 2
    SPEAKING = 3
    HINT_SHOWN = 4
    ANIMATION_STARTED = 5


class SoundPlayer(object):
    __meta__ = ABCMeta

    def __init__(self):
        super(SoundPlayer, self).__init__()
        self._muted = False
        self._enabled = False

    def setMuted(self, value):
        self._muted = value

    def isMuted(self):
        return self._muted

    def setEnabled(self, value):
        self._enabled = value

    def isEnabled(self):
        return self._enabled

    @abstractmethod
    def play(self, event, sndID=None):
        pass

    @abstractmethod
    def stop(self):
        pass

    def isPlaying(self, event, sndID=None):
        return False

    def goToNextChapter(self):
        pass


class NoSound(SoundPlayer):

    def play(self, event, sndID=None):
        pass

    def stop(self):
        pass


class SimpleSoundPlayer(SoundPlayer):

    def play(self, _, sndID=None):
        if sndID is not None:
            SoundGroups.g_instance.playSound2D(sndID)
        else:
            LOG_ERROR('No sound event specified for SimpleSoundPlayer')
        return

    def stop(self):
        pass


class GLOBAL_VAR(object):
    LAST_HISTORY_ID = '_TutorialLastHistoryID'
    SERVICE_MESSAGES_IDS = '_TutorialServiceMessagesIDs'
    PLAYER_VEHICLE_NAME = '_TutorialPlayerVehicleName'
    ALL = (LAST_HISTORY_ID, SERVICE_MESSAGES_IDS, PLAYER_VEHICLE_NAME)


class GLOBAL_FLAG(object):
    IS_FLAGS_RESET = '_TutorialIsFlagsReset'
    SHOW_HISTORY = '_TutorialShowHistory'
    HISTORY_NOT_AVAILABLE = '_TutorialHistoryNotAvailable'
    MODE_IS_AVAILABLE = '_TutorialModeIsAvailable'
    IN_QUEUE = '_InTutorialQueue'
    ALL_BONUSES_RECEIVED = '_AllBonusesReceived'
    MAY_PAWN_PERSONAL_MISSION = '_MayPawnPersonalMission'
    HAVE_NEW_BADGE = '_HaveNewBadge'
    LOBBY_MENU_ITEM_MANUAL = '_LobbyMenuItemManual'
    LOBBY_MENU_ITEM_BOOTCAMP = '_LobbyMenuItemBootcamp'
    HAVE_NEW_SUFFIX_BADGE = '_HaveNewSuffixBadge'
    BADGE_PAGE_HAS_NEW_SUFFIX_BADGE = '_BadgePageHasNewSuffixBadge'
    CREW_BOOKS_ENABLED = '_CrewBooksEnabled'
    COLLECTIBLE_VEHICLE_PREVIEW_ENABLED = '_CollectibleVehiclePreviewEnabled'
    DOGTAGS_ENABLED = '_DogTagsEnabled'
    VEH_POST_PROGRESSION_ENABLED = '_VehPostProgressionEnabled'
    VEH_POST_PROGRESSION_PURCHASABLE = '_VehPostProgressionPurchasable'
    WOTPLUS_ENABLED = '_WotPlusEnabled'
    BATTLE_MATTERS_ENTRY_POINT = '_BattleMattersEntryPoint'
    PERSONAL_RESERVES_AVAILABLE = '_Personal_reserves_available'
    ALL = (IS_FLAGS_RESET,
     SHOW_HISTORY,
     HISTORY_NOT_AVAILABLE,
     IN_QUEUE,
     ALL_BONUSES_RECEIVED,
     MAY_PAWN_PERSONAL_MISSION,
     HAVE_NEW_BADGE,
     HAVE_NEW_SUFFIX_BADGE,
     BADGE_PAGE_HAS_NEW_SUFFIX_BADGE,
     CREW_BOOKS_ENABLED,
     COLLECTIBLE_VEHICLE_PREVIEW_ENABLED,
     DOGTAGS_ENABLED,
     WOTPLUS_ENABLED,
     BATTLE_MATTERS_ENTRY_POINT,
     PERSONAL_RESERVES_AVAILABLE)


class GlobalStorage(object):
    __slots__ = ('attribute',)
    __storage = {}
    __default = {}
    onSetValue = Event.Event()

    def __init__(self, attribute, defaultValue):
        self.attribute = attribute
        if attribute not in self.__storage:
            self.__storage[attribute] = defaultValue
            if attribute in GLOBAL_VAR.ALL:
                self.__default[attribute] = defaultValue

    def __repr__(self):
        return 'GlobalStorage {0:s}: {1!r:s}'.format(self.attribute, self.__storage.get(self.attribute))

    def __set__(self, _, value):
        self.__storage[self.attribute] = value

    def __get__(self, instance, owner=None):
        return self if instance is None else self.__storage[self.attribute]

    def value(self):
        return self.__storage[self.attribute]

    @classmethod
    def setFlags(cls, flags):
        for flag, value in flags.iteritems():
            if flag not in GLOBAL_FLAG.ALL:
                LOG_ERROR('It is not global flag', flag)
                continue
            cls.__storage[flag] = value

    @classmethod
    def clearFlags(cls):
        for flag in GLOBAL_FLAG.ALL:
            if flag in cls.__storage:
                cls.__storage[flag] = False

    @classmethod
    def clearVars(cls):
        for var in GLOBAL_VAR.ALL:
            if var in cls.__storage:
                if var in cls.__default:
                    cls.__storage[var] = cls.__default[var]
                else:
                    cls.__storage[var] = None

        return

    @classmethod
    def all(cls):
        return cls.__storage.copy()

    @classmethod
    def getValue(cls, attribute):
        result = None
        if attribute in cls.__storage:
            result = cls.__storage[attribute]
        return result

    @classmethod
    def setValue(cls, attribute, value, showImmediately=True):
        oldValue = cls.__storage.get(attribute)
        if oldValue != value:
            cls.__storage[attribute] = value
            if showImmediately:
                cls.onSetValue(attribute, value)


class ClientCtx(object):

    @classmethod
    def fetch(cls, *args):
        pass

    @classmethod
    def makeCtx(cls, record):
        pass

    def makeRecord(self):
        pass
