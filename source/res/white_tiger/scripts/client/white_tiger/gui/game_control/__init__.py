# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/__init__.py
from white_tiger.gui.game_control.awards_controller import WhiteTigerQuestsHandler, WhiteTigerPunishHandler
from gui.shared.system_factory import registerAwardControllerHandlers

def registerWhiteTigerAwardControllers():
    registerAwardControllerHandlers((WhiteTigerQuestsHandler, WhiteTigerPunishHandler))


def registerWhiteTigerSMTypes():
    from gui import SystemMessages
    SystemMessages.SM_TYPE.inject(['WTEventProgression', 'WTEventStart'])
