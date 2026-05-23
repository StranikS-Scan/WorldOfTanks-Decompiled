# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/loading_sounds.py
import WWISE
import SoundGroups
from gui.shared import g_eventBus
from gui.shared.events import HasCtxEvent, SharedEvent
DEFAULT_LOADING_SOUND = 'loginscreen_ambient_start'
UE_01_LOGINSCREEN_ENTER_SOUND = 'ue_01_loginscreen_enter'
EVENT_LOADING_SOUND_CHANGE = 'loadingSoundChange'
EVENT_LOADING_SOUND_START = 'loadingSoundStart'
SOUND_ARG = 'sound'

class GameLoadingSoundsListener(object):
    __slots__ = ('__currentSound', '__notLoadedEvent')

    def __init__(self):
        super(GameLoadingSoundsListener, self).__init__()
        g_eventBus.addListener(EVENT_LOADING_SOUND_CHANGE, self.__onChangeSound)
        g_eventBus.addListener(EVENT_LOADING_SOUND_START, self.__onStartLoadingSound)
        self.__currentSound = ''
        self.__notLoadedEvent = None
        return

    def destroy(self):
        g_eventBus.removeListener(EVENT_LOADING_SOUND_CHANGE, self.__onChangeSound)
        g_eventBus.removeListener(EVENT_LOADING_SOUND_START, self.__onStartLoadingSound)

    def __onStartLoadingSound(self, _):
        WWISE.loadLogin()
        SoundGroups.g_instance.playSound2D(UE_01_LOGINSCREEN_ENTER_SOUND)
        if self.__notLoadedEvent:
            self.__playEvent(self.__notLoadedEvent)
            self.__notLoadedEvent = None
        else:
            self.__playEvent(DEFAULT_LOADING_SOUND)
        return

    def __onChangeSound(self, event):
        ctx = event.ctx
        sound = ctx.get(SOUND_ARG, DEFAULT_LOADING_SOUND)
        self.__playEvent(sound)

    def __playEvent(self, sound):
        if SoundGroups.g_instance and sound and sound != self.__currentSound:
            self.__currentSound = sound
            SoundGroups.g_instance.playSound2D(sound)
        else:
            self.__notLoadedEvent = sound


def handleLoadingSoundStartEvent():
    g_eventBus.handleEvent(SharedEvent(eventType=EVENT_LOADING_SOUND_START))


def handleLoadingSoundChangeEvent(sound):
    g_eventBus.handleEvent(HasCtxEvent(eventType=EVENT_LOADING_SOUND_CHANGE, ctx={SOUND_ARG: sound}))
