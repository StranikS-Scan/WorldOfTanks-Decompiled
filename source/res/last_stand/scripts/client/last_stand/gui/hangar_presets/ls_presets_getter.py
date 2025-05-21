# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/hangar_presets/ls_presets_getter.py
from last_stand_common.last_stand_constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from last_stand.gui.scaleform.daapi.view.lobby.header.helpers.controls_helpers import LSLobbyHeaderHelper
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter

class LSPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.LAST_STAND
    _BONUS_TYPES = (ARENA_BONUS_TYPE.LAST_STAND,)
    _LOBBY_HEADER_HELPER = LSLobbyHeaderHelper


class LSMediumPresetsGetter(LSPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.LAST_STAND_MEDIUM
    _BONUS_TYPES = (ARENA_BONUS_TYPE.LAST_STAND_MEDIUM,)


class LSHardPresetsGetter(LSPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.LAST_STAND_HARD
    _BONUS_TYPES = (ARENA_BONUS_TYPE.LAST_STAND_HARD,)
