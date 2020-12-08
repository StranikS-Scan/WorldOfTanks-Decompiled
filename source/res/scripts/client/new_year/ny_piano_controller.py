# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_piano_controller.py
from random import randint
import WWISE
from Event import Event, EventManager
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from skeletons.new_year import INewYearController, IPianoController
from skeletons.gui.shared import IItemsCache
from items.components.ny_constants import ToySettings
_ToysMatch = {ToySettings.FAIRYTALE: 0,
 ToySettings.NEW_YEAR: 1,
 ToySettings.CHRISTMAS: 2,
 ToySettings.ORIENTAL: 3}

class _PianoConstants(object):
    MIN_FIRST_IDLE = 60
    MAX_FIRST_IDLE = 120
    MIN_OTHERS_IDLE = 120
    MAX_OTHERS_IDLE = 240
    MAX_NOVICE_LEVEL = 5
    MAX_ADVANCED_LEVEL = 7
    PIANO_STOP_DELAY = 8


class _PianoSoundStates(object):
    STATE_GROUP = 'STATE_ext_newyear2020_style'
    STATE_FAIRYTALE = 'STATE_ext_newyear2020_style_magic'
    STATE_NEW_YEAR = 'STATE_ext_newyear2020_style_soviet'
    STATE_CHRISTMAS = 'STATE_ext_newyear2020_style_europe'
    STATE_ORIENTAL = 'STATE_ext_newyear2020_style_asia'
    SOUND_STOP_EVENT = 'hangar_newyear_music_stop'
    States = (STATE_FAIRYTALE,
     STATE_NEW_YEAR,
     STATE_CHRISTMAS,
     STATE_ORIENTAL)
    StatesCount = len(States)


_PIANIST_CLICK = 'hangar_newyear_pianist_click'

class PianoController(IPianoController):
    __newYearController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__eventsManager = EventManager()
        self.onLevelUp = Event(self.__eventsManager)
        self.__maxLevel = 0
        self.__currentSetting = 0
        self.__isInited = False
        self.__idleLeft = 0
        self.__notifier = SimpleNotifier(self.__getTimeToNotify, self.__onNotify)
        self.__notify = False

    def init(self):
        super(PianoController, self).init()
        self.__checkLevel()
        self.__idleLeft = randint(_PianoConstants.MIN_FIRST_IDLE, _PianoConstants.MAX_FIRST_IDLE)

    def onLobbyInited(self, event):
        self.__checkLevel()
        self.__start()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def fini(self):
        self.__stop()
        self.__eventsManager.clear()
        super(PianoController, self).fini()

    @staticmethod
    def getStatesCount():
        return _PianoSoundStates.StatesCount

    def getCurrentMusicLevel(self, check=True):
        if check:
            self.__checkLevel()
        musicLevel = 1
        if self.__maxLevel > _PianoConstants.MAX_NOVICE_LEVEL:
            musicLevel += 1
        if self.__maxLevel > _PianoConstants.MAX_ADVANCED_LEVEL:
            musicLevel += 1
        return musicLevel

    def getSoundState(self):
        return _PianoSoundStates.States[self.__currentSetting]

    def getEffectState(self):
        return self.__currentSetting

    def setInitialState(self):
        if not self.__isInited:
            self.__isInited = True
            maxStyle = self.__newYearController.getMaxToysStyle()
            self.__currentSetting = _ToysMatch.get(maxStyle) or 0
        WWISE.WW_setState(_PianoSoundStates.STATE_GROUP, self.getSoundState())

    def isNoMoreIdle(self):
        if not self.__idleLeft:
            self.__idleLeft = randint(_PianoConstants.MIN_OTHERS_IDLE, _PianoConstants.MAX_OTHERS_IDLE)
        self.__idleLeft -= 1
        return self.__idleLeft == 0

    def handlePianoClicked(self):
        self.__currentSetting = (self.__currentSetting + 1) % _PianoSoundStates.StatesCount
        self.__idleLeft = 0
        WWISE.WW_setState(_PianoSoundStates.STATE_GROUP, self.getSoundState())
        WWISE.WW_eventGlobal(_PIANIST_CLICK)

    def __start(self):
        self.__newYearController.onDataUpdated += self.__onDataUpdated

    def __stop(self):
        self.__newYearController.onDataUpdated -= self.__onDataUpdated

    def __checkLevel(self):
        self.__maxLevel = self.__itemsCache.items.festivity.getMaxLevel()

    def __onDataUpdated(self, _):
        oldMusicLevel = self.getCurrentMusicLevel(False)
        newMusicLevel = self.getCurrentMusicLevel(True)
        if newMusicLevel > oldMusicLevel:
            WWISE.WW_eventGlobal(_PianoSoundStates.SOUND_STOP_EVENT)
            self.__notify = True
            self.__notifier.startNotification()

    def __getTimeToNotify(self):
        return _PianoConstants.PIANO_STOP_DELAY if self.__notify else 0

    def __onNotify(self):
        self.__notify = False
        self.__notifier.stopNotification()
        self.__idleLeft = 0
        self.onLevelUp()
