# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/event_squad_button_state_vo.py
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from gui.Scaleform.locale.WT_EVENT import WT_EVENT

class EventSquadButtonStateVO(SquadActionButtonStateVO):

    def _wrongModeMessage(self):
        return (WT_EVENT.SQUADWINDOW_VEHICLE_RESTRICTION, {})
