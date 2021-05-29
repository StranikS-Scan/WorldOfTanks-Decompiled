# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/sound_helpers.py
import SoundGroups
import WWISE
from shared_utils import CONST_CONTAINER

class SliderSoundEvents(CONST_CONTAINER):
    RTPC_PROGRESS_BAR = 'RTPC_ext_ammo_progress_bar'
    SLIDER_SINGLE_PLUS = 'cons_ammo_single_plus'
    SLIDER_SINGLE_MINUS = 'cons_ammo_single_minus'


def playSliderUpdateSound(oldCount, newCount, totalCount):
    WWISE.WW_setRTPCBus(SliderSoundEvents.RTPC_PROGRESS_BAR, newCount * 100.0 / totalCount)
    if newCount > oldCount:
        SoundGroups.g_instance.playSound2D(SliderSoundEvents.SLIDER_SINGLE_PLUS)
    elif newCount < oldCount:
        SoundGroups.g_instance.playSound2D(SliderSoundEvents.SLIDER_SINGLE_MINUS)
