# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadActionButtonStateVO.py
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.prb_control.settings import UNIT_RESTRICTION

class SquadActionButtonStateVO(ActionButtonStateVO):

    def _isEnabled(self, isValid, restriction):
        if not isValid and restriction == UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT:
            return True
        return isValid

    def _getLabel(self):
        if self._playerInfo.isReady:
            label = CYBERSPORT.WINDOW_UNIT_NOTREADY
        else:
            label = CYBERSPORT.WINDOW_UNIT_READY
        return label

    def _getArenaStateStr(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_SQUADINBATTLE, {})

    def _getReadyValidInSlotStateStr(self):
        return (CYBERSPORT.WINDOW_UNIT_MESSAGE_GETNOTREADY, {})

    def _getIdleStateStr(self):
        return ('', {})
