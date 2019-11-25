# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicles/dualgun_sounds.py
import WWISE
import math_utils
import BigWorld
from gui.battle_control.battle_constants import CANT_SHOOT_ERROR
from helpers.CallbackDelayer import CallbackDelayer

class DualGunSoundEvents(object):
    CHARGE_FX = 'gun_rld_dual_charge_FX'
    CHARGE_STARTED = 'gun_rld_dual_charge_start'
    CHARGE_CANCEL = 'gun_rld_dual_charge_cancel'
    CHARGE_FAILED = 'gun_rld_dual_charge_fail'
    CHARGE_PRE = 'gun_rld_dual_charge_pre'
    RTPC_CHARGE_PROGRESS = 'RTPC_ext_gun_rld_dual_charge_progress'
    CHARGE_PROGRESS_STOP = 'gun_rld_dual_charge_progress_loop_stop'
    COOLDOWN_END = 'gun_rld_dual_cooldown_end'
    NOT_ENOUGH_SHELLS = 'gun_rld_dual_charge_no_enough_shells'
    WEAPON_CHANGED = 'gun_rld_dual_wpn_change'
    DAULGUN_RELOAD_SNIPER_SWITCH = 'gun_rld_dual_wpn_switch_sniper_mode'
    CHARGE_SOUND_FX_LENGTH = 1.0
    WEAPON_CHANGED_SOUND_LENGTH = 0.8


class ChargeSoundRTPCInterpolator(CallbackDelayer):

    def __init__(self, interpolationTime=0.0):
        super(ChargeSoundRTPCInterpolator, self).__init__()
        self.__startTime = 0.0
        self.__totalInterpolationTime = interpolationTime
        self.enabled = False

    def enable(self, interpolationTime):
        self.__totalInterpolationTime = interpolationTime
        self.__startTime = BigWorld.timeExact()
        self.delayCallback(0.0, self.__update)
        self.enabled = True

    def disable(self):
        self.__startTime = 0.0
        self.stopCallback(self.__update)
        self.stopCallback(self.disable)
        self.enabled = False
        WWISE.WW_eventGlobal(DualGunSoundEvents.CHARGE_PROGRESS_STOP)

    def __update(self):
        currentTime = BigWorld.timeExact()
        elapsedTime = currentTime - self.__startTime
        interpolationCoefficient = math_utils.linearTween(elapsedTime, 1.0, self.__totalInterpolationTime)
        resultValue = int(math_utils.lerp(0, 100, interpolationCoefficient))
        WWISE.WW_setRTCPGlobal(DualGunSoundEvents.RTPC_CHARGE_PROGRESS, resultValue)
        if elapsedTime > self.__totalInterpolationTime:
            self.delayCallback(0.0, self.disable)
            return 10.0


class DualGunSounds(CallbackDelayer):

    def __init__(self):
        super(DualGunSounds, self).__init__()
        self.__interpolator = ChargeSoundRTPCInterpolator()

    def onComponentDisposed(self):
        self.__interpolator.disable()

    def onChargeStarted(self, timeLeft):
        if timeLeft > 0:
            WWISE.WW_eventGlobal(DualGunSoundEvents.CHARGE_STARTED)
            self.__interpolator.enable(timeLeft)
            timeToStart = timeLeft - DualGunSoundEvents.CHARGE_SOUND_FX_LENGTH
            if timeToStart > 0:
                self.delayCallback(timeToStart, self.__runFXSound)

    def onChargeCanceled(self):
        if self.__interpolator.enabled:
            WWISE.WW_eventGlobal(DualGunSoundEvents.CHARGE_CANCEL)
            self.__interpolator.disable()
        self.stopCallback(self.__runFXSound)

    def onWeaponChanged(self, leftTime):
        if leftTime > 0:
            timeToStart = leftTime - DualGunSoundEvents.WEAPON_CHANGED_SOUND_LENGTH
            if timeToStart > 0:
                self.delayCallback(timeToStart, self.__runChangeWeaponSound)

    def onCooldownEnd(self, leftTime):
        if leftTime > 0:
            self.delayCallback(leftTime, self.__runCooldownEndSound)
            self.__interpolator.disable()

    @staticmethod
    def onSniperCameraTransition():
        WWISE.WW_eventGlobal(DualGunSoundEvents.DAULGUN_RELOAD_SNIPER_SWITCH)

    @staticmethod
    def onPreChargeStarted():
        WWISE.WW_eventGlobal(DualGunSoundEvents.CHARGE_PRE)

    @staticmethod
    def onChargeReleased(canShoot, error, canMakeDualShoot):
        if not canShoot and error == CANT_SHOOT_ERROR.NO_AMMO:
            WWISE.WW_eventGlobal(DualGunSoundEvents.NOT_ENOUGH_SHELLS)
        if not canMakeDualShoot:
            WWISE.WW_eventGlobal(DualGunSoundEvents.CHARGE_FAILED)

    @staticmethod
    def __runFXSound():
        WWISE.WW_eventGlobal(DualGunSoundEvents.CHARGE_FX)

    @staticmethod
    def __runCooldownEndSound():
        WWISE.WW_eventGlobal(DualGunSoundEvents.COOLDOWN_END)

    @staticmethod
    def __runChangeWeaponSound():
        WWISE.WW_eventGlobal(DualGunSoundEvents.WEAPON_CHANGED)
