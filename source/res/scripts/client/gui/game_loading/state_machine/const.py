# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/const.py
import enum
import typing
MINIMUM_PLAYER_LOADING_PROGRESS_BAR_MAX_VALUE = 800
DEFAULT_LOGIN_STATUS_MIN_SHOW_TIME_SEC = 1
LOADING_VIEW_FADE_OUT_DURATION = 0.2
DEFAULT_SLIDE_DURATION = 15
DEFAULT_SLIDE_TRANSITION_DURATION = 0.4
DEFAULT_LOGIN_NEXT_SLIDE_DURATION = 8
DEFAULT_WAITING_TIMEOUT = 10.0

@enum.unique
class GameLoadingStates(str, enum.Enum):
    CLIENT_INIT = 'client.init'
    CLIENT_INIT_LOGOS = 'client.init.logos'
    CLIENT_INIT_LOADING = 'client.init.loading'
    CLIENT_INIT_LOADING_SLIDE = 'client.loading.slide'
    CLIENT_INIT_LOADING_PROGRESS = 'client.loading.progress'
    CLIENT_INIT_LOADING_STATUS = 'client.loading.status'
    CLIENT_INIT_LOADING_STUB = 'client.loading.stub'
    LOGIN_SCREEN = 'login.screen'
    PLAYER_LOADING = 'player.loading'
    PLAYER_LOADING_SLIDE = 'player.loading.slide'
    PLAYER_LOADING_PROGRESS = 'player.loading.progress'
    PLAYER_LOADING_STATUS = 'player.loading.status'
    IDLE = 'idle'


@enum.unique
class GameLoadingStatesEvents(str, enum.Enum):
    LOGOS_SHOWN = 'logos.shown'
    CLIENT_LOADING = 'client.loading'
    LOGIN_SCREEN = 'login.screen'
    PLAYER_LOADING = 'player.loading'
    IDLE = 'idle'


@enum.unique
class ContentState(enum.IntEnum):
    INVISIBLE = 0
    VISIBLE = 1

    @classmethod
    def values(cls):
        return [ obj.value for obj in cls.__members__.values() ]


@enum.unique
class TickingMode(enum.IntEnum):
    MANUAL = 0
    SELF_TICKING = 1
    BOTH = 2
