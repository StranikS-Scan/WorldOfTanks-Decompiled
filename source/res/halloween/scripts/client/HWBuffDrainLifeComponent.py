# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffDrainLifeComponent.py
from __future__ import absolute_import
import random
import weakref
from functools import partial
import BigWorld
from halloween.gui.battle_control.halloween_battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from script_component.DynamicScriptComponent import DynamicScriptComponent
_REPEAT_FIRE_EFFECT_DELAY = 15.0

class HWBuffDrainLifeComponent(DynamicScriptComponent):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HWBuffDrainLifeComponent, self).__init__()
        self.__callbackDelayer = CallbackDelayer()
        self.__isReady = False
        self.__effectListPlayerRef = None
        return

    def onDestroy(self):
        self.entity.events.onAppearanceReady -= self.__onAppearanceReady
        self.__callbackDelayer.destroy()
        self.__stopDrainingLifeEffects()
        if BigWorld.player() and self.__isReady:
            BigWorld.player().onAvatarVehicleChanged -= self.__onAvatarVehicleChanged
        super(HWBuffDrainLifeComponent, self).onDestroy()

    def set_isActive(self, prev):
        self.__updateVisualStatus()

    def set_isShownStatusIcon(self, prev):
        if self.__isReady:
            self.__setDamageIndication(self.isShownStatusIcon)

    def _onAvatarReady(self):
        super(HWBuffDrainLifeComponent, self)._onAvatarReady()
        appearance = self.entity.appearance
        if appearance is None or not appearance.isConstructed:
            self.entity.events.onAppearanceReady += self.__onAppearanceReady
        else:
            self.__onAppearanceReady()
        return

    def __updateVisualStatus(self):
        if not self.__isReady:
            return
        self.__callbackDelayer.clearCallbacks()
        if self.isActive:
            self.__playFireEffect()
        else:
            self.__stopDrainingLifeEffects()

    def __isPlayerVehicle(self, vehicleID):
        player = BigWorld.player()
        if not player:
            return False
        return False if not player.vehicle else vehicleID == player.vehicle.id

    def __setDamageIndication(self, value):
        if not self.__isPlayerVehicle(self.entity.id):
            return
        self._guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HW_DRAIN_LIFE, value)

    def __stopDrainingLifeEffects(self):
        self.__callbackDelayer.clearCallbacks()
        self.__stopFireEffects()
        self.__setDamageIndication(False)

    def __playFireEffect(self):
        vehicle = self.entity
        stages, effects, _ = random.choice(vehicle.typeDescriptor.type.effects['flaming'])
        self.__playRepeatingFireEffect(vehicle, effects, stages)

    def __playRepeatingFireEffect(self, vehicle, effects, stages):
        callback = partial(self.__playRepeatingFireEffect, vehicle, effects, stages)
        self.__callbackDelayer.delayCallback(_REPEAT_FIRE_EFFECT_DELAY, callback)
        if self.__getEffectsListPlayer() is not None:
            self.__fadeFireEffects()
        data = {'entity_id': vehicle.id}
        waitForKeyOff = True
        effectListPlayer = vehicle.appearance.boundEffects.addNew(None, effects, stages, waitForKeyOff, **data)
        self.__effectListPlayerRef = weakref.ref(effectListPlayer)
        return

    def __stopFireEffects(self):
        effectsListPlayer = self.__getEffectsListPlayer()
        if effectsListPlayer is not None:
            effectsListPlayer.stop(forceCallback=True)
            self.__effectListPlayerRef = None
        return

    def __fadeFireEffects(self):
        effectsListPlayer = self.__getEffectsListPlayer()
        if effectsListPlayer is not None:
            effectsListPlayer.keyOff()
            self.__effectListPlayerRef = None
        return

    def __getEffectsListPlayer(self):
        return self.__effectListPlayerRef() if self.__effectListPlayerRef is not None else None

    def __onAppearanceReady(self):
        self.__isReady = True
        if BigWorld.player():
            BigWorld.player().onAvatarVehicleChanged += self.__onAvatarVehicleChanged
        self.__updateVisualStatus()
        self.__setDamageIndication(self.isShownStatusIcon)

    def __onAvatarVehicleChanged(self):
        self.__updateVisualStatus()
        self.__setDamageIndication(self.isShownStatusIcon)
