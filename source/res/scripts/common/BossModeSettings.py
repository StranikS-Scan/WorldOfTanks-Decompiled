# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BossModeSettings.py
from debug_utils import LOG_DEBUG_DEV

class BossModeEvents(object):
    SPAWN_MINE = 'SpawnMine'
    REMOVE_MINE = 'RemoveMine'
    ACTIVATE_MINE = 'ActivateMine'
    SPAWN_HEALTH_POWERUP = 'SpawnHealthPowerup'
    UPDATE_LEVIATHAN_PROGRESS = 'UpdateLeviathanProgress'
    REMOVE_HEALTH_POWERUP = 'RemoveHealthPowerup'
    KILL_CREEPS = 'KillCreeps'


class BossMode:

    def __init__(self, healthThreshold, events):
        self.healthThreshold = healthThreshold
        self.events = events


class BossModeSettings:

    def __init__(self, bossName):
        LOG_DEBUG_DEV('BossModeSettings for', bossName)
        self.boss = bossName
        self.teamNum = 2
        self.phases = []
        self.minionEvents = []
        self.mineDamage = 0
        self.mineRadius = 0
        self.mineDuration = 10
        self.mineEffects = None
        self.mineActivationDelay = 0.0
        self.mineModelActivationDelay = 0.0
        self.healthPowerupRadius = 0
        self.healthPowerupDuration = 10
        self.healthPowerupHealAmount = 500
        self.healthPowerupEffects = None
        self.pathProgressSegments = {}
        self.mineModels = {}
        self.healthPowerupModels = {}
        return

    def setTeamNum(self, teamNum):
        LOG_DEBUG_DEV('Boss Team', teamNum)
        self.teamNum = teamNum

    def addPhase(self, healthThreshold, events):
        LOG_DEBUG_DEV('BossMode', healthThreshold, events)
        self.phases.append(BossMode(healthThreshold, events))

    def addMinionEvent(self, healthThreshold, events):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Minion Event: ', healthThreshold, events)
        self.minionEvents.append(BossMode(healthThreshold, events))

    def setMineDamage(self, damage):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Mine Damage: ', damage)
        self.mineDamage = damage

    def setMineRadius(self, radius):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Mine Radius: ', radius)
        self.mineRadius = radius

    def setMineDuration(self, duration):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Mine Duration: ', duration)
        self.mineDuration = duration

    def addMineModels(self, key, modelName, actionName=None):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Mine Model', key, modelName, actionName)
        if modelName is not None:
            entry = {'modelName': modelName,
             'actionName': actionName}
            if not self.mineModels.has_key(key):
                self.mineModels[key] = [entry]
            else:
                self.mineModels[key].append(entry)
        return

    def setMineEffects(self, effectsSection):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Mine Effects Added: ', effectsSection)
        self.mineEffects = effectsSection

    def setMineActivationDelay(self, activationDelay):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Mine Activation Delay: ', activationDelay)
        self.mineActivationDelay = activationDelay

    def setMineModelActivationDelay(self, modelActivationDelay):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Mine Model Activation Delay: ', modelActivationDelay)
        self.mineModelActivationDelay = modelActivationDelay

    def addHealthPowerupModels(self, key, modelName, actionName=None):
        if modelName is not None:
            entry = {'modelName': modelName,
             'actionName': actionName}
            if not self.healthPowerupModels.has_key(key):
                self.healthPowerupModels[key] = [entry]
            else:
                self.healthPowerupModels[key].append(entry)
        return

    def setHealthPowerupRadius(self, radius):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Health Powerup Radius: ', radius)
        self.healthPowerupRadius = radius

    def setHealthPowerupDuration(self, duration):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Health Powerup Duration: ', duration)
        self.healthPowerupDuration = duration

    def setHealthPowerupHealAmount(self, amount):
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Health Powerup Heal Amount: ', amount)
        self.healthPowerupHealAmount = amount

    def setHealthPowerupEffects(self, effectsSection):
        self.healthPowerupEffects = effectsSection

    def addPathProgressSegment(self, segmentName, startingFraction, endingFraction, segmentLength):
        newValueTuple = (startingFraction, endingFraction, segmentLength)
        self.pathProgressSegments[segmentName] = newValueTuple
        LOG_DEBUG_DEV('[BOSS_MODE_SETTINGS] Add Path Progress Segment - Key: ', segmentName, ' Value: ', newValueTuple)
