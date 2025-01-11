# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/__init__.py


def initProgression():
    from gui.game_control import registerGrinchProgressionGameControllers
    from gui.notifications import registerGPNotifications
    registerGrinchProgressionGameControllers()
    registerGPNotifications()
