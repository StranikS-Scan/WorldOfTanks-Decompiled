# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/progressive_reward/progressive_award_sounds.py
import WWISE
from shared_utils import CONST_CONTAINER

class ProgressiveRewardSoundEvents(CONST_CONTAINER):
    PROGRESSIVE_REWARD_VIEW_GROUP = 'STATE_overlay_hangar_general'
    PROGRESSIVE_REWARD_VIEW_ENTER = 'STATE_overlay_hangar_general_on'
    PROGRESSIVE_REWARD_VIEW_EXIT = 'STATE_overlay_hangar_general_off'
    PROGRESSIVE_REWARD_AWARD_GROUP = 'STATE_overlay_hangar_general'
    PROGRESSIVE_REWARD_AWARD_ENTER = 'STATE_overlay_hangar_general_on'
    PROGRESSIVE_REWARD_AWARD_EXIT = 'STATE_overlay_hangar_general_off'


def setSoundState(groupName, stateName, eventName=None):
    playSound(eventName=eventName)
    WWISE.WW_setState(groupName, stateName)


def playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)
