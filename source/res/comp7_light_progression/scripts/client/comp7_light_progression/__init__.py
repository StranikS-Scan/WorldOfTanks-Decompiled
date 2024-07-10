# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/__init__.py


def initProgression():
    from gui.game_control import registerComp7LightProgressionAwardControllers, registerComp7LightGameControllers
    from gui.gui_constants import registerSystemMessagesTypes
    from messenger.formatters import registerMessengerClientFormatters
    from notification import registerClientNotificationHandlers
    registerSystemMessagesTypes()
    registerComp7LightProgressionAwardControllers()
    registerClientNotificationHandlers()
    registerMessengerClientFormatters()
    registerComp7LightGameControllers()
