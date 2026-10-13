# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffInfinitePeriodicHealComponent.py
from __future__ import absolute_import
import BigWorld
from dyn_components_groups import groupComponent
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from xml_config_specs import StrParam
from HWBuffSequencesComponent import HWBuffSequencesComponent
from shared_utils import nextTick
from vehicle_systems.stricted_loading import makeCallbackWeak

@groupComponent(buffKey=StrParam())
class HWBuffInfinitePeriodicHealComponent(HWBuffSequencesComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWBuffInfinitePeriodicHealComponent, self).__init__()
        self._buffKey = self.groupComponentConfig.buffKey

    def set_isActive(self, prev):
        self._onChangeBuffState()

    def onDestroy(self):
        BigWorld.player().arena.onVehicleHealthChanged -= self._onVehicleHealthChanged
        super(HWBuffInfinitePeriodicHealComponent, self).onDestroy()

    def _onAvatarReady(self):
        super(HWBuffInfinitePeriodicHealComponent, self)._onAvatarReady()
        BigWorld.player().arena.onVehicleHealthChanged += self._onVehicleHealthChanged
        self._onChangeBuffState()

    def _activateEffects(self):
        super(HWBuffInfinitePeriodicHealComponent, self)._activateEffects()
        nextTick(makeCallbackWeak(self._playEffect))()

    def _onChangeBuffState(self):
        hwBattleGuiCtrl = self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            ctx = {'buffKey': self._buffKey,
             'isActive': self.isActive,
             'vehicleID': self.entity.id}
            hwBattleGuiCtrl.buffStateChanged(ctx)
        self._playEffect()

    def _onVehicleHealthChanged(self, vehicleID, attackerID, damage):
        if self.entity.id == vehicleID:
            self._playEffect()

    def _playEffect(self):
        if self.isActive and self.entity.health < self.entity.maxHealth:
            self._startEffects()
        else:
            self._stopEffects()
