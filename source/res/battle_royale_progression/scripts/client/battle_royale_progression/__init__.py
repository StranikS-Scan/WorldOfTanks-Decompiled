# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/__init__.py


def initProgression():
    from gui.game_control import registerBRProgressionAwardControllers, registerBRGameControllers
    from gui.gui_constants import registerSystemMessagesTypes
    from messenger.formatters import registerMessengerClientFormatters
    from notification import registerClientNotificationHandlers
    registerSystemMessagesTypes()
    registerBRProgressionAwardControllers()
    registerClientNotificationHandlers()
    registerMessengerClientFormatters()
    registerBRGameControllers()
