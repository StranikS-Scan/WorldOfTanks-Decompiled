# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/__init__.py


def initProgression():
    from gui.game_control import registerHBProgressionAwardControllers, registerHBGameControllers
    from messenger.formatters import registerMessengerClientFormatters
    from notification import registerClientNotificationHandlers
    registerHBProgressionAwardControllers()
    registerClientNotificationHandlers()
    registerMessengerClientFormatters()
    registerHBGameControllers()
