# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/rts_battles/sound_manager.py
import WWISE
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import CONST_CONTAINER
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID

class Sounds(CONST_CONTAINER):
    PRIME_TIMES_SPACE_NAME = 'rts_prime_times'
    R4_HANGAR_FIRST_SELECT_EVENT = 'r4_hangar_mode_firstEnter'
    R4_HANGAR_ENTER_EVENT = 'r4_hangar_mode_enter'
    R4_HANGAR_EXIT_EVENT = 'r4_hangar_mode_exit'
    R4_HANGAR_PRIME_TIMES_IN = 'r4_hangar_curfew_enter'
    R4_HANGAR_PRIME_TIMES_OUT = 'r4_hangar_curfew_exit'
    R4_REWARD_SCREEN_COLLECTION_ELEMENT = 'r4_hangar_collection_element'
    R4_REWARD_SCREEN_COLLECTION_ALL = 'r4_hangar_collection_all'
    R4_REWARD_SCREEN_COLLECTION_CLOSE = 'r4_hangar_collection_close'
    R4_TUTORIAL_VICTORY = 'gui_hangar_simple_execution_screen'
    R4_TUTORIAL_DEFEAT = 'gui_hangar_neutral_screen'


RTS_PRIME_TIME_SOUND_SPACE = CommonSoundSpaceSettings(name=Sounds.PRIME_TIMES_SPACE_NAME, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=Sounds.R4_HANGAR_PRIME_TIMES_IN, exitEvent=Sounds.R4_HANGAR_PRIME_TIMES_OUT)

class StartStopSoundEvent(object):

    def __init__(self, startEventName, stopEventName):
        self.__startEventName = startEventName
        self.__stopEventName = stopEventName
        self.__isPlaying = False

    def startEvent(self):
        if not self.__isPlaying:
            WWISE.WW_eventGlobal(self.__startEventName)
            self.__isPlaying = True

    def stopEvent(self):
        if self.__isPlaying:
            WWISE.WW_eventGlobal(self.__stopEventName)
            self.__isPlaying = False


class RTSSoundManager(object):
    _appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__isFirstEntrance', '__r4HangarCollectionPage', '__r4ProgressBarAnim', '__r4HangarRosterSetup', '__r4HangarInfoPage', '__RTSSoundModeActive')

    def __init__(self):
        self.__isFirstEntrance = True
        self.__r4HangarCollectionPage = StartStopSoundEvent('r4_hangar_collections_enter', 'r4_hangar_collections_exit')
        self.__r4ProgressBarAnim = StartStopSoundEvent('r4_hangar_ui_progress_bar_start', 'r4_hangar_ui_progress_bar_stop')
        self.__r4HangarRosterSetup = StartStopSoundEvent('r4_hangar_roster_enter', 'r4_hangar_roster_exit')
        self.__r4HangarInfoPage = StartStopSoundEvent('r4_hangar_infoPage_enter', 'r4_hangar_infoPage_exit')
        self.__RTSSoundModeActive = False
        self._appLoader.onGUISpaceLeft += self.__onGUISpaceLeft

    def __del__(self):
        self._appLoader.onGUISpaceLeft -= self.__onGUISpaceLeft

    def setIsFirstEntrance(self, value=True):
        self.__isFirstEntrance = value

    def clear(self):
        self.__isFirstEntrance = True

    def onOpenPage(self):
        self.__r4HangarInfoPage.startEvent()

    def onOpenRosterSetup(self):
        self.__r4HangarRosterSetup.startEvent()

    def onOpenCollectionsPage(self):
        self.__r4HangarCollectionPage.startEvent()

    def onOpenTutorialResultScreen(self, isVictory=False):
        self.onOpenPage()
        if isVictory:
            self.__playSound(Sounds.R4_TUTORIAL_VICTORY)
        else:
            self.__playSound(Sounds.R4_TUTORIAL_DEFEAT)

    def onClosePage(self):
        self.__r4HangarInfoPage.stopEvent()

    def onCloseRosterSetup(self):
        self.__r4HangarRosterSetup.stopEvent()

    def onCollectionProgressBarAnimation(self, isStart):
        if isStart:
            self.__r4ProgressBarAnim.startEvent()
        else:
            self.__r4ProgressBarAnim.stopEvent()

    def onCloseCollectionsPage(self):
        self.__r4HangarCollectionPage.stopEvent()

    def onRewardScreenShow(self, isComplete=False):
        if isComplete:
            self.__playSound(Sounds.R4_REWARD_SCREEN_COLLECTION_ALL)
        else:
            self.__playSound(Sounds.R4_REWARD_SCREEN_COLLECTION_ELEMENT)

    def onRewardScreenClose(self):
        self.__playSound(Sounds.R4_REWARD_SCREEN_COLLECTION_CLOSE)

    def __playSound(self, wwiseEventName, isLoop=False):
        WWISE.WW_eventGlobal(wwiseEventName)

    def onSoundModeChanged(self, isRTSSoundMode):
        if isRTSSoundMode:
            self.__RTSSoundModeActive = isRTSSoundMode
            if self.__isFirstEntrance:
                self.__isFirstEntrance = False
                self.__playSound(Sounds.R4_HANGAR_FIRST_SELECT_EVENT)
            else:
                self.__playSound(Sounds.R4_HANGAR_ENTER_EVENT)
        else:
            if self.__RTSSoundModeActive:
                self.__playSound(Sounds.R4_HANGAR_EXIT_EVENT)
            self.__RTSSoundModeActive = isRTSSoundMode

    def __onGUISpaceLeft(self, spaceID):
        if spaceID != GuiGlobalSpaceID.LOBBY:
            return
        self.__r4HangarCollectionPage.stopEvent()
        self.__r4ProgressBarAnim.stopEvent()
        self.__r4HangarRosterSetup.stopEvent()
        self.__r4HangarInfoPage.stopEvent()
        self.onSoundModeChanged(False)
