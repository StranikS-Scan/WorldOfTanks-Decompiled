# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/sound_constants.py
from __future__ import absolute_import
from enum import Enum

class HangarSoundStates(Enum):
    PLACE = 'STATE_hangar_place'
    SPACE = 'STATE_hangar_space'
    PLACE_GARAGE = 'STATE_hangar_place_garage'
    ALL_VEHICLES_ON = 'STATE_hangar_space_on'
    ALL_VEHICLES_OFF = 'STATE_hangar_space_off'
