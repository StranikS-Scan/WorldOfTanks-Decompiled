# Embedded file name: scripts/client/gui/app_loader/settings.py


class GUI_GLOBAL_SPACE_ID(object):
    UNDEFINED = 0
    WAITING = 1
    INTRO_VIDEO = 2
    LOGIN = 4
    LOBBY = 8
    BATTLE_LOADING = 16
    BATTLE_TUT_LOADING = 32
    FALLOUT_MULTI_TEAM_LOADING = 64
    BATTLE = 128
    BATTLE_LOADING_IDS = (BATTLE_LOADING, BATTLE_TUT_LOADING, FALLOUT_MULTI_TEAM_LOADING)


class DISCONNECT_REASON(object):
    UNDEFINED = 0
    REQUEST = 1
    EVENT = 2
    KICK = 3


class APP_STATE_ID(object):
    NOT_CREATED = 0
    INITIALIZING = 1
    INITIALIZED = 2


class APP_NAME_SPACE(object):
    SF_LOBBY = 'scaleform/lobby'
    SF_BATTLE = 'scaleform/battle'
    SF_LOGITECH = 'scaleform/logiTech'
