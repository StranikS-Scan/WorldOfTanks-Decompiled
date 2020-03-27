# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/tournament/unit/action_handler.py
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.stronghold.unit.actions_handler import StrongholdActionsHandler

class TournamentActionsHandler(StrongholdActionsHandler):

    def showGUI(self):
        g_eventDispatcher.showTournamentWindow()
