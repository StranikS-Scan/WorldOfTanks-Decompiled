# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_game_messages_ctrl.py
from typing import TYPE_CHECKING
from Event import Event
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.game_messages_ctrl import GameMessagesController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if TYPE_CHECKING:
    from client.Vehicle import Vehicle

class EventGameMessagesController(GameMessagesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(EventGameMessagesController, self).__init__(setup)
        self.invalidZoneEntered = Event()
        self.invalidZoneExit = Event()

    def onInvalidZoneEnter(self, sender):
        self.invalidZoneEntered(sender)

    def onInvalidZoneExit(self, sender):
        self.invalidZoneExit(sender)

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_GAME_MESSAGES
