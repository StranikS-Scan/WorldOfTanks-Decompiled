# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/flag_nots.py
from gui.Scaleform.daapi.view.meta.FlagNotificationMeta import FlagNotificationMeta
from gui.Scaleform.genConsts.FLAG_NOTIFICATION_CONSTS import FLAG_NOTIFICATION_CONSTS
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE as _STATE
from gui.battle_control.controllers.flag_nots_ctrl import IFlagNotificationView
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class FlagNotification(FlagNotificationMeta, IFlagNotificationView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def showFlagDelivered(self):
        self.as_setStateS(FLAG_NOTIFICATION_CONSTS.STATE_FLAG_DELIVERED)

    def showFlagDropped(self):
        self.as_setStateS(FLAG_NOTIFICATION_CONSTS.STATE_FLAG_DROPPED)

    def showFlagAbsorbed(self):
        self.as_setStateS(FLAG_NOTIFICATION_CONSTS.STATE_FLAG_ABSORBED)

    def showFlagCaptured(self):
        self.as_setStateS(FLAG_NOTIFICATION_CONSTS.STATE_FLAG_CAPTURED)

    def _populate(self):
        super(FlagNotification, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(FlagNotification, self)._dispose()
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == _STATE.FIRE:
            self.as_setActiveS(not value)
        elif state in (_STATE.SHOW_DESTROY_TIMER, _STATE.SHOW_DEATHZONE_TIMER):
            self.as_setActiveS(False)
        elif state in (_STATE.HIDE_DESTROY_TIMER, _STATE.HIDE_DEATHZONE_TIMER):
            self.as_setActiveS(True)
