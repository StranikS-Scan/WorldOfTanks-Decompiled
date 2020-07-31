# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/loot_drop_object.py
import random
import math
from collections import namedtuple
import Math
import BigWorld
import AnimationSequence
import math_utils
from battleground.components import ModelComponent
from math_utils import Easing
from BombersWing import CompoundBomber, BomberDesc, CurveControlPoint
from Event import Event
from battleground.loot_object import SequenceComponent
from battleground.component_loading import loadComponentSystem, Loader
from battleground.iself_assembler import ISelfAssembler
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from svarog_script.py_component import Component
from svarog_script.script_game_object import ScriptGameObject, ComponentDescriptorTyped, ComponentDescriptor
import Svarog

class DescendSimulator(Component):
    matrix = property(lambda self: self.__matrix)

    def __init__(self, yaw, dropPoint, endPoint, descendTime):
        self.__matrix = math_utils.createRotationMatrix((yaw, 0, 0))
        self.easing = Easing.linearEasing(dropPoint, endPoint, descendTime)
        self.prevTime = BigWorld.time()
        self.tick()

    def tick(self):
        curTime = BigWorld.time()
        self.easing.update(curTime - self.prevTime)
        self.prevTime = curTime
        self.__matrix.translation = self.easing.value


class ParachuteCargo(ScriptGameObject, CallbackDelayer):
    model = ComponentDescriptorTyped(ModelComponent)
    landingAnimation = ComponentDescriptorTyped(SequenceComponent)
    descendSimulator = ComponentDescriptor()
    LANDING_TRIGGER = 'Landed'
    LANDING_ANIMATION_TRIGGER_OFFSET = -0.3

    def __init__(self, yaw, dropPoint, landingPosition, descendTime):
        ScriptGameObject.__init__(self, BigWorld.player().spaceID)
        CallbackDelayer.__init__(self)
        self.descendSimulator = DescendSimulator(yaw, dropPoint, landingPosition, descendTime)
        self.__descendTime = descendTime
        self.__dropPoint = dropPoint

    def activate(self):
        ScriptGameObject.activate(self)
        self.model.compoundModel.position = self.__dropPoint
        self.model.compoundModel.matrix = self.descendSimulator.matrix
        self.landingAnimation.bindToCompound(self.model.compoundModel)
        self.landingAnimation.start()
        self.delayCallback(self.__descendTime + self.LANDING_ANIMATION_TRIGGER_OFFSET, self.__animateLanding)

    def deactivate(self):
        super(ParachuteCargo, self).deactivate()
        if self.landingAnimation is not None:
            self.landingAnimation.stop()
            self.landingAnimation.unbind()
        return

    def destroy(self):
        ScriptGameObject.destroy(self)
        CallbackDelayer.destroy(self)

    def __animateLanding(self):
        if self.landingAnimation is not None:
            self.landingAnimation.setTrigger(self.LANDING_TRIGGER)
        return


class DropPlane(Component, CallbackDelayer):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    TimingConfig = namedtuple('TimingConfig', ('flightStartTime', 'deliveryTime', 'flightEndTime'))
    FLY_TIME_BEFORE_DROP = 20
    FLY_TIME_AFTER_DROP = 10
    UNLOAD_ANIMATION_TIME = 8.0
    FLIGHT_SPEED = 300 / 3.6
    ARRIVAL_VECTOR = Math.Vector3(0, math.sin(math.radians(-30)), math.cos(math.radians(-30)))
    DEPARTURE_VECTOR = Math.Vector3(0, math.sin(math.radians(20)), math.cos(math.radians(20)))
    ARRIVAL_TRAJECTORY_INCLINATION = ARRIVAL_VECTOR * FLY_TIME_BEFORE_DROP * FLIGHT_SPEED
    DEPARTURE_TRAJECTORY_INCLINATION = DEPARTURE_VECTOR * FLY_TIME_AFTER_DROP * FLIGHT_SPEED
    flightYaw = property(lambda self: self.__flightYaw)
    OPEN_CARGO_ANIMATION_TRIGGER = 'OpenCargo'
    CLOSE_CARGO_ANIMATION_TRIGGER = 'CloseCargo'

    def __init__(self, deliveryPoint, dropAltitude, dropTime):
        CallbackDelayer.__init__(self)
        angle = random.random() * 2 * math.pi
        self.__flightYaw = angle
        rotationMatrix = math_utils.createRotationMatrix((angle, 0, 0))
        dropPoint = deliveryPoint + Math.Vector3(0, dropAltitude, 0)
        beginPosition = dropPoint - rotationMatrix.applyVector(self.ARRIVAL_TRAJECTORY_INCLINATION)
        flatFlyVelocity = rotationMatrix.applyToAxis(2) * self.FLIGHT_SPEED
        beginPointDesc = CurveControlPoint(beginPosition, flatFlyVelocity, dropTime - self.FLY_TIME_BEFORE_DROP)
        dropPointDesc = CurveControlPoint(dropPoint, flatFlyVelocity, dropTime)
        dropPlaneConfig = self.__dynamicObjectsCache.getConfig(self.__sessionProvider.arenaVisitor.getArenaGuiType()).getDropPlane()
        spaceId = BigWorld.player().spaceID
        compoundName = 'dropPlaneModel'
        modelAssembler = BigWorld.CompoundAssembler(compoundName, spaceId)
        modelAssembler.addRootPart(dropPlaneConfig.model, 'root')
        animationBuilder = AnimationSequence.Loader(dropPlaneConfig.flyAnimation, spaceId)
        planeDesc = BomberDesc(modelAssembler, dropPlaneConfig.sound, beginPointDesc, dropPointDesc, animationBuilder)
        self.dropPlane = CompoundBomber(planeDesc)
        endPosition = dropPoint + rotationMatrix.applyVector(self.DEPARTURE_TRAJECTORY_INCLINATION)
        self.dropPlane.addControlPoint(endPosition, flatFlyVelocity, dropTime + self.FLY_TIME_AFTER_DROP)
        delayTime = dropTime - BigWorld.time() - self.FLY_TIME_BEFORE_DROP
        self.delayCallback(delayTime, self.__openCargo)
        self.delayCallback(delayTime + self.UNLOAD_ANIMATION_TIME, self.__closeCargo)
        self.prevTime = BigWorld.time()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def destroy(self):
        CallbackDelayer.destroy(self)
        if self.dropPlane is not None:
            self.dropPlane.destroy()
        return

    def __openCargo(self):
        self.dropPlane.setTrigger(DropPlane.OPEN_CARGO_ANIMATION_TRIGGER)

    def __closeCargo(self):
        self.dropPlane.setTrigger(DropPlane.CLOSE_CARGO_ANIMATION_TRIGGER)

    def tick(self):
        curTime = BigWorld.time()
        self.dropPlane.tick(curTime, curTime - self.prevTime)
        self.prevTime = curTime


class PlaneLootAirdrop(ScriptGameObject, CallbackDelayer, ISelfAssembler):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    FLY_TIME_BEFORE_DROP = DropPlane.FLY_TIME_BEFORE_DROP
    FLY_TIME_AFTER_DROP = DropPlane.FLY_TIME_AFTER_DROP
    DESCEND_TIME = 7
    DROP_ALTITUDE = 50
    POST_DELIVERY_CARGO_LIFETIME = 12.0
    cargo = ComponentDescriptor()
    plane = ComponentDescriptor()

    def __init__(self, dropID, deliveryPosition, deliveryTime):
        ScriptGameObject.__init__(self, BigWorld.player().spaceID)
        CallbackDelayer.__init__(self)
        self.owner = Svarog.GameObject(BigWorld.player().spaceID)
        self.owner.activate()
        self.owner.addComponent(self)
        Svarog.addGameObject(BigWorld.player().spaceID, self.owner)
        self.id = dropID
        self.deliveryPosition = deliveryPosition
        self.deliveryTime = deliveryTime + BigWorld.time() - BigWorld.serverTime()
        self.onFlightEnd = Event()

    def start(self, *args, **kwargs):
        planeStartTime = self.deliveryTime - self.FLY_TIME_BEFORE_DROP
        self.delayCallback(planeStartTime - BigWorld.time(), self.__launchPlane)
        dropStartTime = self.deliveryTime - self.DESCEND_TIME
        self.delayCallback(dropStartTime - BigWorld.time(), self.__dropCrate)
        self.inactiveCargo = None
        self.activate()
        return

    def destroy(self):
        if self.inactiveCargo is not None:
            self.inactiveCargo.stopLoading = True
            self.inactiveCargo.destroy()
        self.inactiveCargo = None
        if self.cargo:
            self.cargo.stopLoading = True
        ScriptGameObject.destroy(self)
        CallbackDelayer.destroy(self)
        return

    def __launchPlane(self):
        self.plane = DropPlane(self.deliveryPosition, self.DROP_ALTITUDE, self.deliveryTime - self.DESCEND_TIME)
        self.delayCallback(self.deliveryTime + self.FLY_TIME_AFTER_DROP - BigWorld.time(), self.__processFlightEnd)

    def __dropCrate(self):
        airDropConfig = self.__dynamicObjectsCache.getConfig(self.__sessionProvider.arenaVisitor.getArenaGuiType()).getAirDrop()
        spaceId = BigWorld.player().spaceID
        compoundName = 'crateModel'
        modelAssembler = BigWorld.CompoundAssembler(compoundName, spaceId)
        modelAssembler.addRootPart(airDropConfig.model, 'root')
        animationPath = airDropConfig.dropAnimation
        animationBuilder = AnimationSequence.Loader(animationPath, spaceId)
        dropPoint = self.deliveryPosition + Math.Vector3(0, self.DROP_ALTITUDE, 0)
        crateYaw = 0
        if self.plane is not None:
            crateYaw = self.plane.flightYaw
        self.inactiveCargo = parachuteCargo = ParachuteCargo(crateYaw, dropPoint, self.deliveryPosition, self.DESCEND_TIME)
        loadComponentSystem(parachuteCargo, self.__onCargoLoad, {'model': Loader(modelAssembler),
         'landingAnimation': Loader(animationBuilder)})
        self.delayCallback(self.deliveryTime - BigWorld.time() + self.POST_DELIVERY_CARGO_LIFETIME, self.__killCargo)
        return

    def __onCargoLoad(self, cargo):
        self.cargo = cargo
        self.inactiveCargo = None
        cargo.activate()
        return

    def __killCargo(self):
        self.cargo = None
        return

    def __processFlightEnd(self):
        self.onFlightEnd(self)
        self.plane = None
        Svarog.removeGameObject(self.owner.worldID, self.owner)
        return
