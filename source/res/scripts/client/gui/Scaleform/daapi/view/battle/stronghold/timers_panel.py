# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/stronghold/timers_panel.py
import logging
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.impl import backport
from gui.impl.gen import R
_logger = logging.getLogger(__name__)
_INSPIRE_TIMERS = (BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE,
 BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_CD,
 BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_SOURCE,
 BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_INACTIVATION_SOURCE)
_INSPIRE_TIMERS_MAP = {(True, True): BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_INACTIVATION_SOURCE,
 (True, False): BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_SOURCE,
 (False, True): BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_CD,
 (False, False): BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE}

class StrongholdTimersPanel(TimersPanel):

    def _generateSecondaryTimersData(self):
        data = super(StrongholdTimersPanel, self)._generateSecondaryTimersData()
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_SOURCE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_SOURCE_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SECONDARY_TIMER_UI, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, noiseVisible=False, pulseVisible=True, text=FORTIFICATIONS.INSPIRE_INSPIRING))
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.INSPIRE_INACTIVATION_SOURCE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.INSPIRE_SOURCE_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SECONDARY_TIMER_UI, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, noiseVisible=False, pulseVisible=False, text=FORTIFICATIONS.INSPIRE_INSPIRING))
        return data

    def _updateInspireTimer(self, isSourceVehicle, isInactivation, endTime, duration, primary=True, equipmentID=None):
        _logger.debug('[INSPIRE] %s _updateInspireTimer: isSourceVehicle: %s, isInactivation: %s, endTime: %s, duration: %s, primary: %s', BigWorld.player().id, isSourceVehicle, isInactivation, endTime, duration, primary)
        for timerID in _INSPIRE_TIMERS:
            self._hideTimer(timerID)

        if isInactivation is not None and primary:
            timerID = _INSPIRE_TIMERS_MAP[isSourceVehicle, isInactivation]
            self._showTimer(timerID, duration, BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW, endTime)
            self.as_setSecondaryTimerTextS(timerID, self._getInspireSecondaryTimerText(isSourceVehicle=isSourceVehicle))
        return

    def _getInspireSecondaryTimerText(self, isSourceVehicle=False):
        return backport.text(R.strings.fortifications.inspire.inspiring()) if isSourceVehicle else backport.text(R.strings.fortifications.inspire.inspired())
