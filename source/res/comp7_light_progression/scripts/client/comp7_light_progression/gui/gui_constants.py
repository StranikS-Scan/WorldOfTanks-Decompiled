# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/gui/gui_constants.py
from chat_shared import SYS_MESSAGE_TYPE
from constants_utils import ConstInjector
from messenger import m_constants
SM_TYPE_COMP7_LIGHT_PROGRESSION = 'Comp7LightProgressionNotification'
_SM_TYPES = [SM_TYPE_COMP7_LIGHT_PROGRESSION]

class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    COMP7_LIGHT_PROGRESSION_NOTIFICATIONS = 301


def registerSystemMessagesTypes():
    SYS_MESSAGE_TYPE.inject(_SM_TYPES)
