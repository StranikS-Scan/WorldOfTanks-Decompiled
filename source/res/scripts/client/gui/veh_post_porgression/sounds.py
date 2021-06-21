# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_porgression/sounds.py
from shared_utils import CONST_CONTAINER
import WWISE

def playSound(eventName):
    WWISE.WW_eventGlobal(eventName)


class Sounds(CONST_CONTAINER):
    MODIFICATION_DESTROY = 'ev_pp_modification_destroy'
    MODIFICATION_MOUNT = 'ev_pp_modification_mount'
    SETUP_SWITCH = 'ev_pp_setup_switch'
    GAMEPLAY_SETUP_SWITCH = 'ev_pp_gameplay_setup_switch'
