# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadActionButtonStateVO.py
from gui.Scaleform.daapi.view.lobby.rally.ActionButtonStateVO import ActionButtonStateVO
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.game_control import getFalloutCtrl
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.server_events import g_eventsCache
from gui.shared.formatters.ranges import toRomanRangeString
from helpers import int2roman

class SquadActionButtonStateVO(ActionButtonStateVO):

    def _isEnabled(self, isValid, restriction):
        if not isValid and restriction == UNIT_RESTRICTION.FALLOUT_NOT_ENOUGH_PLAYERS:
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

    def _getFalloutVehLevelStr(self):
        if self._extra is None:
            return
        else:
            config = g_eventsCache.getFalloutConfig(self._extra.eventType)
            requiredLevelStr = int2roman(config.vehicleLevelRequired)
            return (CYBERSPORT.WINDOW_UNIT_MESSAGE_FALLOUTLEVEL, {'level': requiredLevelStr})

    def _getFalloutVehMinStr(self):
        if self._extra is None:
            return
        else:
            config = g_eventsCache.getFalloutConfig(self._extra.eventType)
            allowedLevelsList = list(config.allowedLevels)
            if len(allowedLevelsList) > 1:
                return (CYBERSPORT.WINDOW_UNIT_MESSAGE_FALLOUTMIN_LEVELRANGE, {'level': toRomanRangeString(allowedLevelsList, 1)})
            return (CYBERSPORT.WINDOW_UNIT_MESSAGE_FALLOUTMIN_REQUIREDLEVEL, {'level': int2roman(config.vehicleLevelRequired)})
            return

    def _getFalloutVehBrokenStr(self):
        return ('#cyberSport:window/unit/message/falloutGroupNotReady', {})
