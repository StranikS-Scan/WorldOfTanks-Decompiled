# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/const.py
import typing
import enum
MINIMUM_PLAYER_LOADING_PROGRESS_BAR_MAX_VALUE = 800
DEFAULT_LOGIN_STATUS_MIN_SHOW_TIME_SEC = 1
LOADING_VIEW_FADE_OUT_DURATION = 0.2
DEFAULT_SLIDE_DURATION = 15
DEFAULT_SLIDE_TRANSITION_DURATION = 0.4
DEFAULT_LOGIN_NEXT_SLIDE_DURATION = 8

@enum.unique
class GameLoadingStates(str, enum.Enum):
    LOADING_LOGOS = 'loading.logos'
    CLIENT_LOADING = 'client.loading'
    CLIENT_LOADING_SLIDE = 'client.loading.slide'
    CLIENT_LOADING_PROGRESS = 'client.loading.progress'
    CLIENT_LOADING_STATUS = 'client.loading.status'
    LOGIN_SCREEN = 'login.screen'
    PLAYER_LOADING = 'player.loading'
    PLAYER_LOADING_SLIDE = 'player.loading.slide'
    PLAYER_LOADING_PROGRESS = 'player.loading.progress'
    PLAYER_LOADING_STATUS = 'player.loading.status'
    IDL = 'idl'


@enum.unique
class GameLoadingStatesEvents(str, enum.Enum):
    LOGOS_SHOWN = 'logos.shown'
    CLIENT_LOADING = 'client.loading'
    LOGIN_SCREEN = 'login.screen'
    PLAYER_LOADING = 'player.loading'
    IDL = 'idl'


@enum.unique
class ContentState(enum.IntEnum):
    INVISIBLE = 0
    VISIBLE = 1

    @classmethod
    def values(cls):
        return [ obj.value for obj in cls.__members__.values() ]
