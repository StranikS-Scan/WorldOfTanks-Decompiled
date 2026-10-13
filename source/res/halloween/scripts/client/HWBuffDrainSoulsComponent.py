# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffDrainSoulsComponent.py
from __future__ import absolute_import
import BigWorld
import GenericComponents
from halloween.gui.battle_control.halloween_battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from HWBuffSequencesComponent import HWBuffSequencesComponent
from dyn_components_groups import groupComponent
from xml_config_specs import StrParam
from helpers.CallbackDelayer import CallbackDelayer
_ANIMATOR_STATUS_START = 1.0
_ANIMATOR_STATUS_END = 0.0
_START_ANIMATION_DELAY = 0.1

@groupComponent(statusName=StrParam())
class HWBuffDrainSoulsComponent(HWBuffSequencesComponent):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWBuffDrainSoulsComponent, self).__init__()
        self.__callbackDelayer = CallbackDelayer()

    def onDestroy(self):
        self.__stopAura()
        self.__callbackDelayer.destroy()
        super(HWBuffDrainSoulsComponent, self).onDestroy()

    def set_isActive(self, prev):
        self.__updateVisualStatus(True)

    def set_isShownStatusIcon(self, prev):
        if self._isReady:
            self.__setSoulsIndication(self.isShownStatusIcon)

    def _onAvatarReady(self):
        super(HWBuffDrainSoulsComponent, self)._onAvatarReady()
        self.__updateVisualStatus(False)
        self.__setSoulsIndication(self.isShownStatusIcon)

    def _activateEffects(self):
        self.__callbackDelayer.clearCallbacks()
        super(HWBuffDrainSoulsComponent, self)._activateEffects()

    def _onAvatarVehicleChanged(self):
        super(HWBuffDrainSoulsComponent, self)._onAvatarVehicleChanged()
        self.__setSoulsIndication(self.isShownStatusIcon)

    def __updateVisualStatus(self, canStopAura):
        if not self._isReady:
            return
        if self.isActive:
            self.__startAura()
        elif canStopAura:
            self.__stopAura()

    def __stopAura(self):
        self.__callbackDelayer.clearCallbacks()
        self.__setAnimatorStatus(_ANIMATOR_STATUS_END)
        self.__setSoulsIndication(False)

    def __startAura(self):
        self.__callbackDelayer.delayCallback(_START_ANIMATION_DELAY, self.__startAuraDelayed)

    def __startAuraDelayed(self):
        self.__setAnimatorStatus(_ANIMATOR_STATUS_START)

    def __setAnimatorStatus(self, value):
        for go in self._gameObjects:
            if go is None or not go.valid:
                continue
            animator = go.findWrite(GenericComponents.AnimatorComponent)
            if animator:
                statusName = self.groupComponentConfig.statusName
                animator.setFloatParam(statusName, value)

        return

    def __setSoulsIndication(self, value):
        if not self.__isPlayerVehicle(self.entity.id):
            return
        self._guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HW_DRAIN_SOULS, value)

    def __isPlayerVehicle(self, vehicleID):
        player = BigWorld.player()
        if not player:
            return False
        return False if not player.vehicle else vehicleID == player.vehicle.id
