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
__all__ = ('StartReqs', 'BonusesRequester', 'SoundPlayer', 'GlobalStorage', 'SOUND_EVENT')

class StartReqs(object):
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)

    def __del__(self):
        LOG_MEMORY('StartReqs deleted: {0:>s}'.format(self))

    def isEnabled(self):
        return False

    def prepare(self, ctx):
        raise NotImplementedError

    def process(self, descriptor, ctx):
        raise NotImplementedError


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


class GLOBAL_FLAG(object):
    MAY_PAWN_PERSONAL_MISSION = '_MayPawnPersonalMission'
    HAVE_NEW_BADGE = '_HaveNewBadge'
    LOBBY_MENU_ITEM_MANUAL = '_LobbyMenuItemManual'
    LOBBY_MENU_ITEM_BOOTCAMP = '_LobbyMenuItemBootcamp'
    HAVE_NEW_SUFFIX_BADGE = '_HaveNewSuffixBadge'
    BADGE_PAGE_HAS_NEW_SUFFIX_BADGE = '_BadgePageHasNewSuffixBadge'
    COLLECTIBLE_VEHICLE_PREVIEW_ENABLED = '_CollectibleVehiclePreviewEnabled'
    DOGTAGS_ENABLED = '_DogTagsEnabled'
    VEH_POST_PROGRESSION_ENABLED = '_VehPostProgressionEnabled'
    HANGAR_VEH_POST_PROGRESSION_PURCHASABLE = '_HangarVehPostProgressionPurchasable'
    RESEARCH_VEH_POST_PROGRESSION_PURCHASABLE = '_ResearchVehPostProgressionPurchasable'
    PERSONAL_RESERVES_AVAILABLE = '_Personal_reserves_available'
    ALL = (MAY_PAWN_PERSONAL_MISSION,
     HAVE_NEW_BADGE,
     HAVE_NEW_SUFFIX_BADGE,
     BADGE_PAGE_HAS_NEW_SUFFIX_BADGE,
     COLLECTIBLE_VEHICLE_PREVIEW_ENABLED,
     DOGTAGS_ENABLED,
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
