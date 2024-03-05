# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common/bonus_caps_extension.py
import constants_utils
from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE, QUEUE_TYPE, PREBATTLE_TYPE
ATTR_NAME = 'COSMIC_EVENT'

def attrValidator(personality):
    constants_utils.checkAttrNameExist(ATTR_NAME, [ARENA_GUI_TYPE,
     ARENA_BONUS_TYPE,
     QUEUE_TYPE,
     PREBATTLE_TYPE], personality)
