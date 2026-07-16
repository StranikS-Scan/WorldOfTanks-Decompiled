# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/propellant_gun/mechanic_models.py
from __future__ import absolute_import, division
import typing
import BigWorld
from constants import PROPELLANT_GUN_STATE
from gui.shared.utils.decorators import ReprInjector
from math_utils import lerp
from vehicles.mechanics.gun_mechanics.propellant_gun.mechanic_interfaces import IPropellantGunComponentParams, IPropellantGunMechanicState
if typing.TYPE_CHECKING:
    from items.components.shared_components import PropellantGunParams

@ReprInjector.simple('chargePerSec', 'dischargePerSec', 'maxCharge', 'maxOvercharge')
class PropellantGunComponentParams(IPropellantGunComponentParams):

    def __init__(self, chargePerSec, dischargePerSec, maxCharge, maxOvercharge, stages, forbiddenShells):
        super(PropellantGunComponentParams, self).__init__()
        self.__chargePerSec = chargePerSec
        self.__dischargePerSec = dischargePerSec
        self.__stages = stages
        self.__maxCharge = maxCharge
        self.__maxOvercharge = maxOvercharge
        self.__forbiddenShells = forbiddenShells

    @classmethod
    def fromMechanicParams(cls, params):
        return cls(params.chargingPerSec, params.dischargingPerSec, params.maxCharge, params.maxOvercharge if params.maxOvercharge else params.maxCharge, params.chargeStages, params.forbiddenShells)

    @property
    def chargePerSec(self):
        return self.__chargePerSec

    @property
    def dischargePerSec(self):
        return self.__dischargePerSec

    @property
    def maxCharge(self):
        return self.__maxCharge

    @property
    def maxOvercharge(self):
        return self.__maxOvercharge

    @property
    def stages(self):
        return self.__stages

    @property
    def forbiddenShells(self):
        return self.__forbiddenShells


@ReprInjector.simple('state', 'currentStage', 'currentCharge', 'currentThreshold', 'isOvercharge', 'isAvailable', 'isUsableShell', 'isCharged')
class PropellantGunMechanicState(IPropellantGunMechanicState):

    def __init__(self, state, stageID, chargeProgress, isOvercharge, isSwitchCooldownActive, updateTime, isForbiddenShell, lastShotTimestamp, lastShotCharge, params):
        self.__state = state
        self.__stageID = stageID
        self.__chargeProgress = chargeProgress
        self.__isOvercharge = isOvercharge
        self.__isSwitchCooldownActive = isSwitchCooldownActive
        self.__updateTime = updateTime
        self.__isForbiddenShell = isForbiddenShell
        self.__params = params
        self.__overchargeStageCount = len([ stage for stage in self.__params.stages if stage.isOvercharge ])
        self.__lastShotTimestamp = lastShotTimestamp
        self.__lastShotCharge = lastShotCharge

    def __eq__(self, other):
        return all((other.__dict__[key] == value for key, value in self.__dict__.items() if key != '_PropellantGunMechanicState__updateTime'))

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(tuple((value for key, value in self.__dict__.items() if key != '_PropellantGunMechanicState__updateTime')))

    @classmethod
    def fromComponentStatus(cls, status, params, isForbiddenShell=None):
        return cls(status.state, status.chargeStageID, status.chargeProgress, bool(status.isOverchargeEnabled), bool(status.isSwitchCooldownActive), status.updateTimestamp, bool(status.isForbiddenShell) if isForbiddenShell is None else isForbiddenShell, status.lastShotTimestamp, status.lastShotCharge, params)

    @property
    def lastShotTimestamp(self):
        return self.__lastShotTimestamp

    @property
    def lastShotCharge(self):
        return self.__lastShotCharge / self.__params.maxOvercharge

    @property
    def state(self):
        return self.__state

    @property
    def currentStage(self):
        return self.__stageID

    @property
    def currentCharge(self):
        if self.__state in PROPELLANT_GUN_STATE.STATIC_STATES:
            return self.__chargeProgress
        chargeProgress = self.__chargeProgress
        deltaTime = BigWorld.serverTime() - self.__updateTime
        if deltaTime > 0.0:
            limit = self.currentThreshold
            if self.__state == PROPELLANT_GUN_STATE.CHARGING:
                chargeProgress = min(chargeProgress + deltaTime * self.__params.chargePerSec, limit)
            else:
                chargeProgress = max(chargeProgress - deltaTime * self.__params.dischargePerSec, limit)
        return chargeProgress

    @property
    def currentThreshold(self):
        return self.__params.maxOvercharge if self.__isOvercharge else self.__params.maxCharge

    @property
    def isOvercharge(self):
        return self.__isOvercharge

    @property
    def isAvailable(self):
        return not self.__isSwitchCooldownActive

    @property
    def isMaxOverCharged(self):
        return self.currentCharge == self.__params.maxOvercharge

    @property
    def isMaxCharged(self):
        return self.currentCharge >= self.__params.maxCharge

    @property
    def isLastStage(self):
        unusedStages = 0 if self.__isOvercharge else self.__overchargeStageCount
        return self.__stageID == len(self.__params.stages) - unusedStages - 1

    @property
    def isLastChargeStage(self):
        return self.__stageID == len(self.__params.stages) - self.__overchargeStageCount - 1

    @property
    def isUsableShell(self):
        return not self.__isForbiddenShell

    @property
    def timeLeft(self):
        if self.__state in PROPELLANT_GUN_STATE.STATIC_STATES:
            return -1.0
        deltaTime = BigWorld.serverTime() - self.__updateTime
        targetCharge = self.__params.maxCharge if self.__stageID < len(self.__params.stages) - self.__overchargeStageCount else self.__params.maxOvercharge
        if self.__state == PROPELLANT_GUN_STATE.CHARGING:
            chargeTime = (targetCharge - self.__chargeProgress) / self.__params.chargePerSec
        else:
            chargeTime = (self.__chargeProgress - targetCharge) / self.__params.dischargePerSec
        return max(chargeTime - deltaTime, 0.0)

    def getCurrentDamageFactor(self, progress=None):
        progress = self.__chargeProgress if progress is None else progress
        stage = self.__params.stages[self.__stageID]
        maxProgress = stage.maxCharge
        minProgress = self.__params.stages[self.__stageID - 1].maxCharge if self.__stageID > 0 else 0
        damageFactor = lerp(stage.damageFactorLimits.minFactor, stage.damageFactorLimits.maxFactor, (progress - minProgress) / (maxProgress - minProgress))
        return damageFactor

    def isTransition(self, other):
        return self.state != other.state
