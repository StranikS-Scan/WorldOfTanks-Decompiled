# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/__init__.py
from chat_shared import SYS_MESSAGE_TYPE
from battle_royale_progression_common.battle_royale_progression_constants import SM_TYPES

def registerSystemMessagesTypes():
    SYS_MESSAGE_TYPE.inject(SM_TYPES)


def initProgression():
    registerSystemMessagesTypes()
    from gui.game_control import registerBRProgressionAwardControllers, registerBRGameControllers
    registerBRProgressionAwardControllers()
    registerBRGameControllers()
    from notification import registerClientNotificationHandlers
    registerClientNotificationHandlers()
    from messenger.formatters import registerMessengerServerFormatters
    registerMessengerServerFormatters()
