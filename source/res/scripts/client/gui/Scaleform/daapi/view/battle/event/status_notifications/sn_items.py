# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/status_notifications/sn_items.py
from battle_royale.gui.Scaleform.daapi.view.battle.status_notifications.sn_items import TimerSN, _OverturnedBaseSN
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R

class OverturnedSN(_OverturnedBaseSN):

    def __init__(self, updateCallback):
        super(OverturnedSN, self).__init__(updateCallback)
        self._vo['description'] = backport.text(R.strings.battle_royale.timersPanel.halfOverturned())

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED

    def _getSupportedLevel(self):
        pass


class BombCaptureSN(TimerSN):

    def __init__(self, updateCallback):
        super(BombCaptureSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.event.bombCapture.indicator())
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_BOMB_CAPTURE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_BOMB_CAPTURE

    def _update(self, value):
        leftTime, endTime, totalTime = value
        if leftTime > 0:
            self._updateTimeParams(totalTime, endTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)


class BombCarrySN(TimerSN):

    def __init__(self, updateCallback):
        super(BombCarrySN, self).__init__(updateCallback)
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_BOMB_CARRY

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_BOMB_CARRY

    def _update(self, value):
        leftTime, endTime, totalTime, isPaused, timerGUID = value
        self._vo['additionalInfo'] = str(timerGUID)
        if not isPaused and leftTime > 0:
            self._updateTimeParams(totalTime, endTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)


class BombAbsorbSN(TimerSN):

    def __init__(self, updateCallback):
        super(BombAbsorbSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.event.bombAbsorb.indicator())
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_BOMB_ABSORB

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_BOMB_ABSORB

    def _update(self, value):
        leftTime, endTime, totalTime = value
        if leftTime > 0:
            self._updateTimeParams(totalTime, endTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)


class BombDeploySN(TimerSN):

    def __init__(self, updateCallback):
        super(BombDeploySN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.event.bombDeploy.indicator())
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_BOMB_DEPLOY

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_BOMB_DEPLOY

    def _update(self, value):
        leftTime, endTime, totalTime = value
        if leftTime > 0:
            self._updateTimeParams(totalTime, endTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)
