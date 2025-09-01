# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/status_notifications/sn_items.py
import typing
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.status_notifications.sn_items import TimerSN
from gui.impl import backport
from story_mode.gui.battle_control.battle_constant import VEHICLE_VIEW_STATE
from story_mode.gui.scaleform.genConsts.STORY_MODE_NOTIFICATIONS_TIMER_TYPES import STORY_MODE_NOTIFICATIONS_TIMER_TYPES
from story_mode_common.story_mode_constants import RECON_ABILITY

class ReconAbilitySN(TimerSN):

    def _getEquipmentName(self):
        return RECON_ABILITY

    def getItemID(self):
        pass

    def getViewTypeID(self):
        return STORY_MODE_NOTIFICATIONS_TIMER_TYPES.RECON_ABILITY

    def _getDescription(self, value):
        return backport.text(value)

    def _update(self, equipmentInfo):
        if not equipmentInfo:
            self._setVisible(False)
            return
        self._setVisible(True)
        self._updateText(equipmentInfo['text'])
        self._updateTimeParams(equipmentInfo['totalTime'], equipmentInfo['finishTime'])
        self._sendUpdate()


class DisableShotSN(TimerSN):

    def start(self):
        super(DisableShotSN, self).start()
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.SCC_DISABLE_SHOT

    def getViewTypeID(self):
        return STORY_MODE_NOTIFICATIONS_TIMER_TYPES.SCC_DISABLE_SHOT

    def _update(self, duration):
        if duration > 0.0:
            endTime = BigWorld.serverTime() + duration
            self._updateTimeParams(duration, endTime)
            self._setVisible(True)
        else:
            self._setVisible(False)
