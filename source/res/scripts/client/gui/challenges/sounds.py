# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/challenges/sounds.py
from __future__ import absolute_import
from enum import Enum
from gui.sounds.filters import States, StatesGroup
from sound_gui_manager import CommonSoundSpaceSettings

class ChallengesSounds(str, Enum):
    REWARD_SCREEN = 'bp_reward_screen'


CHALLENGE_AWARDS_SOUND_SPACE = CommonSoundSpaceSettings(name=StatesGroup.OVERLAY_HANGAR_GENERAL, entranceStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_ON}, exitStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=ChallengesSounds.REWARD_SCREEN, exitEvent='')
