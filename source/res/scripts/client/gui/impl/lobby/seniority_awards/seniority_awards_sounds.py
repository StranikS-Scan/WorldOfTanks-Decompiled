# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/seniority_awards_sounds.py
import WWISE
from shared_utils import CONST_CONTAINER

class LootBoxViewEvents(CONST_CONTAINER):
    ENTRY_VIEW_ENTER = 'gui_lootbox_logistic_center_ambience_on'
    ENTRY_VIEW_EXIT = 'gui_lootbox_logistic_center_ambience_off'
    BENGAL_FIRE_OFF = 'gui_lootbox_logistic_center_bengal_fire_off'


class SeniorityInfoViewEvents(CONST_CONTAINER):
    ENTRY_VIEW_ENTER = 'gui_hangar_award_info_page_enter'
    ENTRY_VIEW_EXIT = 'gui_hangar_award_info_page_exit'


def playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)
