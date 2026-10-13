# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleDetector.py
from __future__ import absolute_import
from constants import BigWorld
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class HWVehicleDetector(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onDestroy(self):
        self.__fireEvent()
        vehStateCtrl = self.guiSessionProvider.shared.vehicleState
        if vehStateCtrl:
            vehStateCtrl.onVehicleControlling -= self._onVehicleControlling
        avatar = BigWorld.player()
        if avatar:
            avatar.onAvatarVehicleChanged -= self._onAvatarVehicleChanged
        super(HWVehicleDetector, self).onDestroy()

    def set_indicator(self, prev):
        self._onCheckDistanceToFollower()

    def _onAvatarReady(self):
        super(HWVehicleDetector, self)._onAvatarReady()
        vehStateCtrl = self.guiSessionProvider.shared.vehicleState
        if vehStateCtrl:
            vehStateCtrl.onVehicleControlling += self._onVehicleControlling
        avatar = BigWorld.player()
        if avatar:
            avatar.onAvatarVehicleChanged += self._onAvatarVehicleChanged
        self._onCheckDistanceToFollower()

    def _onVehicleControlling(self, vehicle):
        self._onCheckDistanceToFollower()

    def _onCheckDistanceToFollower(self):
        avatar = BigWorld.player()
        if not avatar:
            self.__fireEvent()
            return
        vehicle = avatar.getVehicleAttached()
        if not vehicle:
            self.__fireEvent()
            return
        if vehicle.id != self.entity.id:
            return
        self.__fireEvent(self.indicator)

    def _onAvatarVehicleChanged(self):
        self._onCheckDistanceToFollower()

    def __fireEvent(self, indicator=0):
        hwBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            ctx = {'indicator': indicator}
            hwBattleGuiCtrl.vehicleDetectorChangeDistance(ctx)
