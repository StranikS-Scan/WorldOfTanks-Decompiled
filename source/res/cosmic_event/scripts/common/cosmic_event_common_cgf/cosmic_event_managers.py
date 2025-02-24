# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common_cgf/cosmic_event_managers.py
import BigWorld
import functools
import CGF
import random
import typing
from collections import deque
from constants import IS_CELLAPP, ARENA_PERIOD
from debug_utils import LOG_DEBUG_DEV
from wotdecorators import condition
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, Rule, registerRule, registerManager, tickGroup
from cosmic_event_common.cosmic_event_common import ScoreEvents
from cosmic_event_components import CosmicEventImpulseComponent, CosmicEventNameComponent
from GenericComponents import TransformComponent
from Math import Vector3
if IS_CELLAPP:
    from Vehicle import Vehicle
    from helpers import getArena
    from VehicleImpulseScheduler import clampImpulse
    from GeyserSplash import createGeyserSplash
if typing.TYPE_CHECKING:
    from typing import Dict
_TICKING_PERIOD = 0.1

class BoosterType(object):
    SPRINGBOARD = 'board'
    GEYSER = 'geyser'


class SpringboardsActivationMode(object):
    RANDOM = 'random'
    MANUAL = 'manual'
    PRESETS = 'presets'


_SPRING_BOARD_EFFECT_COMPONENT_NAME = 'SpringboardEffectComponent'
_SPRING_BOARD_EFFECT_COMPONENT_KEY_NAME = 'springboardEffectComponent'

class CosmicEventPhysicsManager(CGF.ComponentManager):
    ifBoostersEnabled = condition('isBoostersEnabled')
    ifBoostersEnabledSafe = condition('isBoostersEnabledSafe')
    ifSpringBoardsEnabled = condition('isSpringBoardsEnabled')
    ifGeysersEnabled = condition('isGeysersEnabled')

    def __init__(self):
        super(CosmicEventPhysicsManager, self).__init__()
        self.__arena = None
        self.__boostersConfig = {}
        self.__springboardsSettings = {}
        self.__geysersSettings = []
        self.__springboards = {}
        self.__geysers = {}
        self.__emptyEntities = {}
        self.__startBattleTime = None
        LOG_DEBUG_DEV('[cosmic_event_managers]: CosmicEventPhysicsManager was inited')
        return

    def activate(self):
        self.__arena = getArena(self.spaceID)
        if not self.__arena:
            return
        else:
            self.__arena.events.onPeriodChange += self.__onArenaPeriodChange
            self.__boostersConfig = self.__arena.additionalParams.get('cosmic_boosters_config', None)
            self.__initSpringBoardsSettings()
            self.__initGeysersSettings()
            for go, comp, transform in CGF.Query(self.spaceID, (CGF.GameObject, CosmicEventNameComponent, TransformComponent)):
                if comp.name.startswith(BoosterType.SPRINGBOARD):
                    self.__springboards[comp.name] = go
                    emptyEntity = BigWorld.createEntity('EmptyEntity', self.spaceID, transform.position, Vector3(0, 0, 0), {})
                    if emptyEntity:
                        emptyEntity.createDynamicComponent(_SPRING_BOARD_EFFECT_COMPONENT_NAME)
                    self.__emptyEntities[comp.name] = emptyEntity
                if comp.name.startswith(BoosterType.GEYSER):
                    self.__geysers[comp.name] = go

            return

    def deactivate(self):
        if self.__arena:
            self.__arena.events.onPeriodChange -= self.__onArenaPeriodChange
            self.__arena = None
        return

    def destroy(self):
        self.__boostersConfig = None
        self.__springboardsSettings = None
        self.__geysersSettings = None
        self.__springboards = None
        self.__geysers = None
        for entity in self.__emptyEntities.itervalues():
            if not entity.isDestroyed:
                entity.destroy()

        self.__emptyEntities = None
        self.__startBattleTime = None
        return

    @property
    def isBoostersEnabled(self):
        return self.__boostersConfig.get('isEnabled', False)

    @property
    def isBoostersEnabledSafe(self):
        arena = getArena(self.spaceID)
        if not arena:
            return False
        boostersConfig = arena.additionalParams.get('cosmic_boosters_config', {})
        return boostersConfig.get('isEnabled', False)

    @property
    def isSpringBoardsEnabled(self):
        return False if not self.__boostersConfig else self.__boostersConfig.get('springboards', {}).get('isEnabled', False)

    @property
    def isGeysersEnabled(self):
        return False if not self.__boostersConfig else self.__boostersConfig.get('geysers', {}).get('isEnabled', False)

    @onAddedQuery(CGF.GameObject, CosmicEventImpulseComponent)
    @ifBoostersEnabledSafe
    def onAdded(self, go, impulseComponent):
        LOG_DEBUG_DEV('[cosmic_event_managers]: CosmicEventImpulseComponent was created on go with id = %s' % go.id)
        trigger = impulseComponent.trigger()
        if not trigger:
            return
        wrappedCallback = functools.partial(self.__applyImpulse, impulseComponent)
        impulseComponent.reactionID = trigger.addEnterReaction(wrappedCallback)

    @onRemovedQuery(CGF.GameObject, CosmicEventImpulseComponent)
    @ifBoostersEnabledSafe
    def onRemoved(self, go, impulseComponent):
        LOG_DEBUG_DEV('[cosmic_event_managers]: CosmicEventImpulseComponent was removed from go = %s' % go.id)
        trigger = impulseComponent.trigger()
        if not trigger:
            return
        trigger.removeEnterReaction(impulseComponent.reactionID)

    @tickGroup('Simulation', updatePeriod=_TICKING_PERIOD)
    @ifBoostersEnabled
    def onTick(self):
        if not self.__startBattleTime:
            return
        timePassed = BigWorld.time() - self.__startBattleTime
        self.__processSpringboards(timePassed)
        self.__processGeysers(timePassed)

    def __initSpringBoardsSettings(self):
        if not self.__boostersConfig:
            return
        config = self.__boostersConfig.get('springboards', {})
        turnOnTime = deque(config.get('turnOnTime', []))
        turnOffTime = deque(config.get('turnOffTime', []))
        self.__springboardsSettings = {'turnOnTime': turnOnTime,
         'turnOffTime': turnOffTime}

    def __initGeysersSettings(self):
        if not self.__boostersConfig:
            return
        config = self.__boostersConfig.get('geysers', {})
        for preset in config.get('presets', []):
            turnOnTime = deque(preset.get('turnOnTime', []))
            turnOffTime = deque(preset.get('turnOffTime', []))
            names = preset.get('names', [])
            self.__geysersSettings.append({'turnOnTime': turnOnTime,
             'turnOffTime': turnOffTime,
             'names': names})

    @ifSpringBoardsEnabled
    def __processSpringboards(self, timePassed):
        if not self.__springboardsSettings:
            return
        self.__triggerCallbackIfTimeHasCome(self.__springboardsSettings.get('turnOnTime', []), timePassed, self.__activateSpringboards)
        self.__triggerCallbackIfTimeHasCome(self.__springboardsSettings.get('turnOffTime', []), timePassed, self.__deactivateSpringboards)

    @ifGeysersEnabled
    def __processGeysers(self, timePassed):
        for setting in self.__geysersSettings:
            geysers = setting.get('names', [])
            activateGeysersCb = functools.partial(self.__activateGeysers, geysers)
            deactivateGeysersCb = functools.partial(self.__deactivateGeysers, geysers)
            self.__triggerCallbackIfTimeHasCome(setting.get('turnOnTime', None), timePassed, activateGeysersCb)
            self.__triggerCallbackIfTimeHasCome(setting.get('turnOffTime', None), timePassed, deactivateGeysersCb)

        return

    def __activateSpringboards(self):
        mode = self.__boostersConfig.get('springboards', {}).get('mode', None)
        processor = self.__getSpringboardsActivationProcessor(mode)
        if processor:
            processor()
        return

    def __deactivateSpringboards(self):
        for go in self.__springboards.itervalues():
            if go.isValid():
                self.__setIsActiveForBooster(go, isActive=False)

    def __activateGeysers(self, geysers):
        for geyser in geysers:
            go = self.__geysers.get(geyser, None)
            if not go:
                continue
            self.__setIsActiveForBooster(go, isActive=True)

        return

    def __deactivateGeysers(self, geysers):
        for geyser in geysers:
            go = self.__geysers.get(geyser, None)
            if not go:
                continue
            self.__setIsActiveForBooster(go, isActive=False)

        return

    def __getSpringboardsActivationProcessor(self, mode):
        processors = {SpringboardsActivationMode.RANDOM: self.__activateSpringboardsRandomly,
         SpringboardsActivationMode.MANUAL: self.__activateSpringboardsManually,
         SpringboardsActivationMode.PRESETS: self.__activateSpringboardsByPresets}
        return processors.get(mode, None)

    def __activateSpringboardsRandomly(self):
        randomBoardsCount = self.__boostersConfig.get('springboards', {}).get('random', 0)
        boardsSize = len(self.__springboards)
        if randomBoardsCount < 0 or randomBoardsCount > boardsSize:
            randomBoardsCount = boardsSize
        boardsToActivate = set(random.sample(self.__springboards, randomBoardsCount))
        for board in boardsToActivate:
            go = self.__springboards.get(board, None)
            if not go:
                continue
            self.__setIsActiveForBooster(go, isActive=True)

        return

    def __activateSpringboardsManually(self):
        boardsToActivate = self.__boostersConfig.get('springboards', {}).get('manual', None)
        if not boardsToActivate:
            return
        else:
            for board in boardsToActivate:
                go = self.__springboards.get(board, None)
                if not go:
                    continue
                self.__setIsActiveForBooster(go, isActive=True)

            return

    def __activateSpringboardsByPresets(self):
        presets = self.__boostersConfig.get('springboards', {}).get('presets', None)
        if not presets:
            return
        else:
            preset = random.choice(presets)
            for board in preset:
                go = self.__springboards.get(board, None)
                if not go:
                    continue
                self.__setIsActiveForBooster(go, isActive=True)

            return

    def __setIsActiveForBooster(self, go, isActive=False):
        if not go.isValid():
            return
        impulseComp = go.findComponentByType(CosmicEventImpulseComponent)
        nameComponent = go.findComponentByType(CosmicEventNameComponent)
        if impulseComp:
            impulseComp.isActive = isActive
        if not nameComponent:
            return
        if isActive:
            LOG_DEBUG_DEV('[cosmic_event_managers]: booster %s was turned on' % nameComponent.name)
        else:
            LOG_DEBUG_DEV('[cosmic_event_managers]: booster %s was turned off' % nameComponent.name)

    def __triggerCallbackIfTimeHasCome(self, triggerPeriods, timePassed, callback, *args, **kwargs):
        if triggerPeriods and timePassed >= triggerPeriods[0]:
            callback(*args, **kwargs)
            triggerPeriods.popleft()

    def __onArenaPeriodChange(self, period, *_):
        if period == ARENA_PERIOD.BATTLE:
            self.__startBattleTime = BigWorld.time()

    def __applyImpulse(self, impulseComp, who, where):
        if not impulseComp.isActive:
            return
        vehicle = self.__getVehicleFromGO(who)
        if not vehicle:
            return
        physics = vehicle.mover.physics
        vehMass = physics.mass
        velocity = physics.velocity
        velocityLimit = self.__boostersConfig.get('velocityLimit', 200.0)
        impulse = impulseComp.impulseDirection * impulseComp.massCoef * vehMass
        impulse = clampImpulse(impulse, vehMass, velocity, velocityLimit)
        physics.applyImpulseToCoM(impulse)
        self.__onImpulseApplied(where, vehicle.id)
        LOG_DEBUG_DEV('[cosmic_event_managers]: __applyImpulse was triggerred on go = %s' % who.id)

    def __getVehicleFromGO(self, obj):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        if not hierarchyManager:
            return None
        else:
            vehicleGO = hierarchyManager.getTopMostParent(obj)
            vehicle = vehicleGO.findComponentByType(Vehicle)
            return None if not vehicle or vehicle.status < 0 else vehicle

    def __onImpulseApplied(self, booster, vehicleID):
        comp = booster.findComponentByType(CosmicEventNameComponent)
        if comp is None:
            return
        else:
            if comp.name.startswith(BoosterType.SPRINGBOARD):
                self.__addPointsForSpringboardApply(vehicleID)
                entity = self.__emptyEntities.get(comp.name, None)
                self.__startSpringboardEffect(entity)
            elif comp.name.startswith(BoosterType.GEYSER):
                transform = booster.findComponentByType(TransformComponent)
                if self.__arena is None:
                    return
                config = self.__arena.ArenaCosmicEventComponent.config
                splashHeight = config.get('effects', {}).get('geyserSplashEffect', {}).get('splashHeight', 0)
                if transform is not None:
                    createGeyserSplash(booster.spaceID, transform.position + Vector3(0, splashHeight, 0), Vector3(0, 0, 0), {})
            return

    def __addPointsForSpringboardApply(self, vehicleID):
        if not self.__arena:
            return
        scoreSystem = self.__arena.ArenaCosmicEventComponent.scoreSystem
        scoreSystem.addPoints(vehicleID, ScoreEvents.BOOST_ME)

    def __startSpringboardEffect(self, entity):
        if entity is None:
            return
        else:
            component = entity.dynamicComponents.get(_SPRING_BOARD_EFFECT_COMPONENT_KEY_NAME)
            if component is not None:
                component.timeApply = BigWorld.time()
            return


@registerRule
class CosmicEventPhysicsManagerRule(Rule):
    category = 'Cosmic'
    domain = CGF.DomainOption.DomainAll

    @registerManager(CosmicEventPhysicsManager, domain=CGF.DomainOption.DomainServer)
    def cosmicEventPhysicsManager(self):
        return None
