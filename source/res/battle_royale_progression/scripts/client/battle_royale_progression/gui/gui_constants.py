# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/gui_constants.py
from chat_shared import SYS_MESSAGE_TYPE
from constants_utils import ConstInjector
from messenger import m_constants
SM_TYPE_BR_PROGRESSION = 'BRProgressionNotification'
_SM_TYPES = [SM_TYPE_BR_PROGRESSION]

class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    BR_PROGRESSION_NOTIFICATIONS = 300


def registerSystemMessagesTypes():
    SYS_MESSAGE_TYPE.inject(_SM_TYPES)
