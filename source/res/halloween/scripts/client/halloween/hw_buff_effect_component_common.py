# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/hw_buff_effect_component_common.py
from __future__ import absolute_import
import BigWorld
from halloween_common.halloween_constants import HWBuffSequenceVisibilityMode
from script_component.DynamicScriptComponent import DynamicScriptComponent
from aih_constants import CTRL_MODE_NAME

class HWBuffEffectComponentCommon(DynamicScriptComponent):
    _SNIPER_MODES = (CTRL_MODE_NAME.SNIPER, CTRL_MODE_NAME.DUAL_GUN)

    def __init__(self):
        super(HWBuffEffectComponentCommon, self).__init__()
        self._isReady = False
        self._isSniperModeAvailable = self.__checkSniperModeAvailable()

    def onDestroy(self):
        if self._isSniperModeAvailable:
            BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged
        if self._isReady:
            self._isReady = False
            BigWorld.player().onAvatarVehicleChanged -= self._onAvatarVehicleChanged
            self._deactivateEffects()
        super(HWBuffEffectComponentCommon, self).onDestroy()

    @property
    def _isActive(self):
        return True

    @property
    def _isInSniperMode(self):
        return BigWorld.player().inputHandler.ctrlModeName in self._SNIPER_MODES

    @property
    def _componentConfigs(self):
        raise NotImplementedError

    def _onAvatarReady(self):
        super(HWBuffEffectComponentCommon, self)._onAvatarReady()
        self._isReady = True
        if self._isSniperModeAvailable:
            BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged
        BigWorld.player().onAvatarVehicleChanged += self._onAvatarVehicleChanged
        self._updateEffectsStatus()

    def _activateEffects(self):
        raise NotImplementedError

    def _deactivateEffects(self):
        pass

    def _updateEffectsStatus(self):
        if not self._isReady:
            return
        if self._isActive:
            self._activateEffects()
        else:
            self._deactivateEffects()

    def _isVehicleObservedByAvatar(self):
        avatar = BigWorld.player()
        if not avatar:
            return False
        vehicle = avatar.getVehicleAttached()
        return vehicle == self.entity

    def _isVisible(self, param):
        visibleTo = getattr(HWBuffSequenceVisibilityMode, param.upper())
        if visibleTo == HWBuffSequenceVisibilityMode.ALL:
            return True
        if visibleTo == HWBuffSequenceVisibilityMode.SELF and self._isVehicleObservedByAvatar():
            return True
        return True if visibleTo == HWBuffSequenceVisibilityMode.OTHERS and not self._isVehicleObservedByAvatar() else False

    def _needsListenToSniperMode(self, visibleTo):
        return self._isSniperModeAvailable and not self._isVisible(visibleTo)

    def _onAvatarVehicleChanged(self):
        self._updateEffectsStatus()

    def _onSniperModeChanged(self, isEnabled):
        raise NotImplementedError

    def __checkSniperModeAvailable(self):
        for config in self._componentConfigs:
            visibleTo = getattr(HWBuffSequenceVisibilityMode, config.sniperModeVisibleTo.upper())
            if visibleTo != HWBuffSequenceVisibilityMode.ALL:
                return True

        return False

    def __onCameraChanged(self, mode, currentVehicleId=None):
        self._onSniperModeChanged(mode in self._SNIPER_MODES)
