# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/status_notifications/sn_items.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.sn_items import TimerSN, HalfOverturnedSN, StaticDeathZoneSN
from last_stand.gui.battle_control.ls_battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from last_stand.gui.scaleform.genConsts.LS_BATTLE_NOTIFICATIONS_TIMER_TYPES import LS_BATTLE_NOTIFICATIONS_TIMER_TYPES as _LSTYPES
from helpers.CallbackDelayer import CallbackDelayer

class _LSLocalizationProvider(sn_items.LocalizationProvider):

    @property
    def _stringResource(self):
        return R.strings.last_stand_battle.statusNotificationTimers


class LSHalfOverturnedSN(_LSLocalizationProvider, HalfOverturnedSN):

    def _getDescription(self, value=None):
        return backport.text(self._stringResource.overturned())


class LSStaticDeathZoneSN(StaticDeathZoneSN):

    def getViewTypeID(self):
        return _LSTYPES.LS_DEATH_ZONE


class LSPersonalDeathZoneSN(_LSLocalizationProvider, TimerSN):

    def __init__(self, updateCallback):
        super(LSPersonalDeathZoneSN, self).__init__(updateCallback)
        self.__callbackDelayer = CallbackDelayer()

    def destroy(self):
        self.__callbackDelayer.destroy()
        super(LSPersonalDeathZoneSN, self).destroy()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PERSONAL_DEATHZONE

    def getViewTypeID(self):
        return _LSTYPES.LS_PERSONAL_DEATH_ZONE

    def _getDescription(self, value):
        return backport.text(self._stringResource.personalDeathZone())

    def _update(self, value):
        self.__callbackDelayer.clearCallbacks()
        visible, strikeDelay, launchTime = value
        if visible:
            finishTime = launchTime + strikeDelay
            self._updateTimeParams(strikeDelay, finishTime)
            if strikeDelay > 0:
                self.__callbackDelayer.delayCallback(finishTime - BigWorld.serverTime(), self.__hideTimer)
            self._isVisible = True
            self._sendUpdate()
            return
        self._setVisible(False)

    def __hideTimer(self):
        params = (self._isVisible, 0, 0)
        self._update(params)
