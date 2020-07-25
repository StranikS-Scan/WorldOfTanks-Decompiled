# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/arena_equipment_component.py
from collections import namedtuple
from functools import partial
import logging
import BigWorld
import Event
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS, ARENA_GUI_TYPE
from debug_utils import LOG_ERROR_DEV
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from gui.battle_control.matrix_factory import makeVehicleEntityMP
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from smoke_screen import SmokeScreen
from AffectComponent import RepairAffectComponent, TrapAffectComponent
_logger = logging.getLogger(__name__)

class EffectData(object):

    class EFFECT_PERIOD(CONST_CONTAINER):
        EXPOSED = 0
        INACTIVATION = 1
        OVER = 2

    TimerTuple = namedtuple('TimerTuple', ('period', 'callbackID'))
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicleID, startTime, endTime, visualSettings, inactivationStartTime=None, inactivationEndTime=None, primary=True, radius=None, senderKey=None, equipmentID=None):
        self.vehicleID = vehicleID
        self.startTime = startTime
        self.endTime = endTime
        self.visualSettings = visualSettings
        self.inactivationStartTime = inactivationStartTime
        self.inactivationEndTime = inactivationEndTime
        self.radius = radius
        self.primary = primary
        self.senderKey = senderKey
        self.equipmentID = equipmentID
        self.__timerTuple = None
        return

    def updateTerrainCircle(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        isAlly = arenaDP and arenaDP.isAllyTeam(arenaDP.getVehicleInfo(self.vehicleID).team)
        vehicle = BigWorld.entities.get(self.vehicleID)
        if vehicle is not None and self.radius is not None:
            effectSettings = self.visualSettings.get('ally') if isAlly else self.visualSettings.get('enemy')
            if effectSettings is not None:
                vehicle.appearance.showTerrainCircle(self.radius, effectSettings)
        return

    @property
    def isActive(self):
        return self.__timerTuple is not None and self.__timerTuple.callbackID is not None

    def setNextCallback(self, func):
        time = BigWorld.serverTime()
        if self.__timerTuple is None or self.__timerTuple.period is None:
            nextPeriod, nextTime = self.getNextPeriodAndStartTime(time, None)
        elif self.__timerTuple.callbackID is not None:
            BigWorld.cancelCallback(self.__timerTuple.callbackID)
            nextPeriod, nextTime = self.getNextPeriodAndStartTime(time, self.__timerTuple.period - 1)
        else:
            nextPeriod, nextTime = self.getNextPeriodAndStartTime(time, self.__timerTuple.period)
        self.__timerTuple = self.TimerTuple(period=nextPeriod, callbackID=BigWorld.callback(nextTime - time, partial(self.__invokeCallback, func, nextPeriod)))
        return

    def cancelCallback(self):
        if self.__timerTuple is not None and self.__timerTuple.callbackID is not None:
            BigWorld.cancelCallback(self.__timerTuple.callbackID)
            self.__timerTuple = None
        return

    def destroy(self):
        vehicle = BigWorld.entities.get(self.vehicleID)
        if vehicle is not None and self.radius is not None:
            vehicle.appearance.hideTerrainCircle()
        if self.__timerTuple is not None and self.__timerTuple.callbackID is not None:
            BigWorld.cancelCallback(self.__timerTuple.callbackID)
        self.__timerTuple = None
        return

    def getNextPeriodAndStartTime(self, currentTime, currentPeriod=None):
        periods = ((self.EFFECT_PERIOD.EXPOSED, self.startTime), (self.EFFECT_PERIOD.INACTIVATION, self.inactivationStartTime), (self.EFFECT_PERIOD.OVER, self.inactivationEndTime))
        if currentPeriod is not None:
            nextPeriod = min(currentPeriod + 1, self.EFFECT_PERIOD.OVER)
            return periods[nextPeriod]
        else:
            return next((period for period in periods if period[1] > currentTime), periods[self.EFFECT_PERIOD.OVER])

    def __invokeCallback(self, func, period):
        self.__timerTuple = self.__timerTuple._replace(callbackID=None)
        func(self, period)
        return


InspireArgs = namedtuple('InspireArgs', ('isSourceVehicle', 'isInactivation', 'endTime', 'duration', 'primary', 'equipmentID'))
HealPointArgs = namedtuple('HealPointArgs', ('isSourceVehicle', 'isInactivation', 'endTime', 'duration', 'senderKey'))

class InspireArgsAdapter(InspireArgs):

    def __new__(cls, isSourceVehicle, isInactivation, endTime, duration, primary, _, equipmentID):
        return super(InspireArgsAdapter, cls).__new__(cls, isSourceVehicle, isInactivation, endTime, duration, primary, equipmentID)


class HealPointArgsAdapter(HealPointArgs):

    def __new__(cls, isSourceVehicle, isInactivation, endTime, duration, _, senderKey, __):
        return super(HealPointArgsAdapter, cls).__new__(cls, isSourceVehicle, isInactivation, endTime, duration, senderKey)


class Effect(object):

    def __init__(self, name, args, vehicleViewState, feedbackEventID, visualSettings, exposedVehicles=None, providingVehicles=None):
        self.name = name
        self.args = args
        self.vehicleViewState = vehicleViewState
        self.feedbackEventID = feedbackEventID
        self.visualSettings = visualSettings
        self.exposedVehicles = exposedVehicles if exposedVehicles is not None else dict()
        self.providingVehicles = providingVehicles if providingVehicles is not None else dict()
        return

    def destroy(self):
        for exposedVehicle in (data for data in self.exposedVehicles.itervalues() if data is not None):
            exposedVehicle.destroy()

        self.exposedVehicles.clear()
        for providingVehicle in (data for data in self.providingVehicles.itervalues() if data is not None):
            providingVehicle.destroy()

        self.providingVehicles.clear()


class ArenaEquipmentComponent(ClientArenaComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.onSmokeScreenStarted = Event.Event(self._eventManager)
        self.onSmokeScreenEnded = Event.Event(self._eventManager)
        self.__smokeScreen = dict()
        self.__healingEffect = None
        self.__inspiringEffect = None
        self.__repairPointEffect = None
        return

    def activate(self):
        super(ArenaEquipmentComponent, self).activate()
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.SMOKE, '', self.__onSmokeScreenUpdated)
        dynamicObjects = self.__dynamicObjectsCache.getConfig(BigWorld.player().arenaGuiType)
        if dynamicObjects is not None:
            self.__inspiringEffect = Effect('inspire', InspireArgsAdapter, VEHICLE_VIEW_STATE.INSPIRE, FEEDBACK_EVENT_ID.VEHICLE_INSPIRE, dynamicObjects.getInspiringEffect())
            self.__healingEffect = Effect('healPoint', HealPointArgsAdapter, VEHICLE_VIEW_STATE.HEALING, FEEDBACK_EVENT_ID.VEHICLE_HEAL_POINT, dynamicObjects.getHealPointEffect())
            if BigWorld.player().arenaGuiType == ARENA_GUI_TYPE.BATTLE_ROYALE:
                self.__repairPointEffect = Effect('repairPoint', HealPointArgsAdapter, VEHICLE_VIEW_STATE.REPAIR_POINT, FEEDBACK_EVENT_ID.VEHICLE_REPAIR_POINT, dynamicObjects.getRepairPointEffect())
        return

    def deactivate(self):
        super(ArenaEquipmentComponent, self).deactivate()
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.SMOKE, '', self.__onSmokeScreenUpdated)
        self.__smokeScreen.clear()
        if self.__inspiringEffect is not None:
            self.__inspiringEffect.destroy()
        if self.__healingEffect is not None:
            self.__healingEffect.destroy()
        if self.__repairPointEffect is not None:
            self.__repairPointEffect.destroy()
        return

    def __removeEffect(self, vehicleId, effect):
        needsRemove = False
        data = effect.providingVehicles.pop(vehicleId, None)
        if data:
            needsRemove |= data.isActive
            data.destroy()
        data = effect.exposedVehicles.pop(vehicleId, None)
        if data:
            needsRemove |= data.isActive
            data.destroy()
        if needsRemove:
            noneArgs = effect.args(None, None, None, None, None, None, None)
            attachedVehicle = BigWorld.player().getVehicleAttached()
            isAttachedVehicle = attachedVehicle and vehicleId == attachedVehicle.id
            if isAttachedVehicle:
                self.sessionProvider.invalidateVehicleState(effect.vehicleViewState, noneArgs._asdict())
            else:
                ctrl = self.sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateBuffEffect(effect.feedbackEventID, vehicleId, noneArgs._asdict())
        return

    def __updateExposedToEffect(self, vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, primary, equipmentID, effect, isInfluenceZone):
        exposedVehicleData = effect.exposedVehicles.get(vehicleID, None)
        if startTime is None:
            if exposedVehicleData is not None:
                exposedVehicleData.startTime = exposedVehicleData.endTime = exposedVehicleData.inactivationStartTime = exposedVehicleData.inactivationEndTime = 0
                providingVehicleData = effect.providingVehicles.get(vehicleID, None)
                if providingVehicleData is not None:
                    exposedVehicleData.destroy()
                    del effect.exposedVehicles[vehicleID]
                else:
                    self.__checkAffectComponent(vehicleID, RepairAffectComponent, isInfluenceZone)
                    self.__restartEffectData(exposedVehicleData, effect, isSource=False, atPeriod=EffectData.EFFECT_PERIOD.OVER)
            return
        else:
            if exposedVehicleData is None:
                effect.exposedVehicles[vehicleID] = exposedVehicleData = EffectData(vehicleID=vehicleID, startTime=startTime, endTime=endTime, visualSettings=effect.visualSettings, inactivationStartTime=inactivationStartTime, inactivationEndTime=inactivationEndTime, primary=primary, senderKey=senderKey, equipmentID=equipmentID)
            else:
                exposedVehicleData.startTime = startTime
                exposedVehicleData.endTime = endTime
                exposedVehicleData.inactivationStartTime = inactivationStartTime
                exposedVehicleData.inactivationEndTime = inactivationEndTime
                exposedVehicleData.senderKey = senderKey
                exposedVehicleData.equipmentID = equipmentID
            self.__checkAffectComponent(vehicleID, RepairAffectComponent, isInfluenceZone)
            self.__restartEffectData(exposedVehicleData, effect, isSource=False)
            return

    def __checkAffectComponent(self, vehicleID, affectComponent, isInfluenceZone):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle and vehicle.isAlive():
            gameObject = vehicle.appearance
            if gameObject.findComponentByType(affectComponent) is not None:
                if not isInfluenceZone:
                    curAffectComponent = gameObject.findComponentByType(affectComponent)
                    gameObject.removeComponent(curAffectComponent)
                    if curAffectComponent.hasDebuff:
                        vehicle.onDebuffEffectApplied(False)
                return
            if isInfluenceZone:
                gameObject.createComponent(affectComponent, gameObject, vehicle.isPlayerVehicle, BigWorld.player().spaceID)
                curAffectComponent = gameObject.findComponentByType(affectComponent)
                if curAffectComponent.hasDebuff:
                    vehicle.onDebuffEffectApplied(True)
        return

    def _updateEffectSource(self, vehicleID, startTime, endTime, inactivationDelay, effectSourceRadius, effect):
        providingVehicleData = effect.providingVehicles.get(vehicleID, None)
        if startTime is None:
            if providingVehicleData is not None:
                providingVehicleData.startTime = providingVehicleData.endTime = providingVehicleData.inactivationStartTime = providingVehicleData.inactivationEndTime = 0
                self.__restartEffectData(providingVehicleData, effect, isSource=True, atPeriod=EffectData.EFFECT_PERIOD.OVER)
            return
        else:
            exposedVehicleData = effect.exposedVehicles.get(vehicleID, None)
            if exposedVehicleData is not None:
                exposedVehicleData.cancelCallback()
            if providingVehicleData is None:
                effect.providingVehicles[vehicleID] = providingVehicleData = EffectData(vehicleID=vehicleID, startTime=startTime, endTime=endTime, visualSettings=effect.visualSettings, inactivationStartTime=endTime, inactivationEndTime=endTime + inactivationDelay if endTime is not None else None, radius=effectSourceRadius)
            else:
                providingVehicleData.startTime = startTime
                providingVehicleData.endTime = endTime
                providingVehicleData.inactivationStartTime = endTime
                providingVehicleData.inactivationEndTime = endTime + inactivationDelay if endTime is not None else None
                providingVehicleData.radius = effectSourceRadius
            self.__restartEffectData(providingVehicleData, effect, isSource=True)
            return

    def removeInspire(self, vehicleID):
        self.__removeEffect(vehicleID, self.__inspiringEffect)

    def removeHealPoint(self, vehicleID):
        self.__removeEffect(vehicleID, self.__healingEffect)

    def removeRepairPoint(self, vehicleID):
        self.__removeEffect(vehicleID, self.__repairPointEffect)

    def updateInspired(self, vehicleID, startTime, endTime, inactivationStartTime, inactivationEndTime, primary, equipmentID):
        self.__updateExposedToEffect(vehicleID, None, startTime, endTime, inactivationStartTime, inactivationEndTime, primary, equipmentID, self.__inspiringEffect, False)
        return

    def updateHealing(self, vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime):
        self.__updateExposedToEffect(vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, True, None, self.__healingEffect, False)
        return

    def updateHealOverTime(self, vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, isInfluenceZone):
        self.__updateExposedToEffect(vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, True, None, self.__repairPointEffect, isInfluenceZone)
        return

    def updateDebuff(self, vehicleID, isInfluenceZone):
        self.__checkAffectComponent(vehicleID, TrapAffectComponent, isInfluenceZone)

    def updateInspiringSource(self, vehicleID, startTime, endTime, inactivationDelay, inspireSourceRadius):
        self._updateEffectSource(vehicleID, startTime, endTime, inactivationDelay, inspireSourceRadius, self.__inspiringEffect)

    def updateHealingSource(self, vehicleID, startTime, endTime, inactivationDelay, healingSourceRadius):
        self._updateEffectSource(vehicleID, startTime, endTime, inactivationDelay, healingSourceRadius, self.__healingEffect)

    def __evaluateExposedData(self, data, period, effect):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        vehicleID = data.vehicleID
        isAttachedVehicle = attachedVehicle and vehicleID == attachedVehicle.id
        isSourceVehicle = effect.providingVehicles.get(vehicleID, None) is not None
        if period == EffectData.EFFECT_PERIOD.EXPOSED:
            args = effect.args(isSourceVehicle, False, data.endTime, data.endTime - BigWorld.serverTime(), data.primary, data.senderKey, data.equipmentID)
            data.setNextCallback(partial(self.__evaluateExposedData, effect=effect))
        elif period == EffectData.EFFECT_PERIOD.INACTIVATION:
            args = effect.args(False, True, data.inactivationEndTime, data.inactivationEndTime - data.inactivationStartTime, data.primary, data.senderKey, data.equipmentID)
            data.setNextCallback(partial(self.__evaluateExposedData, effect=effect))
        else:
            args = effect.args(None, None, None, None, None, None, None)
            data.destroy()
            del effect.exposedVehicles[data.vehicleID]
        if args:
            if isAttachedVehicle:
                self.sessionProvider.invalidateVehicleState(effect.vehicleViewState, args._asdict())
            else:
                ctrl = self.sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateBuffEffect(effect.feedbackEventID, vehicleID, args._asdict())
        return

    def __evaluateEffectSourceData(self, data, period, effect):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        vehicleID = data.vehicleID
        isAttachedVehicle = attachedVehicle and vehicleID == attachedVehicle.id
        if period == EffectData.EFFECT_PERIOD.EXPOSED:
            args = effect.args(True, False, data.endTime, data.endTime - data.startTime, data.primary, data.senderKey, data.equipmentID)
            if isAttachedVehicle:
                self.sessionProvider.invalidateVehicleState(effect.vehicleViewState, args._asdict())
            else:
                ctrl = self.sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateBuffEffect(effect.feedbackEventID, vehicleID, args._asdict())
            data.updateTerrainCircle()
            data.setNextCallback(partial(self.__evaluateEffectSourceData, effect=effect))
        else:
            data.destroy()
            del effect.providingVehicles[vehicleID]
            exposedVehicleData = effect.exposedVehicles.get(vehicleID, None)
            if exposedVehicleData is not None:
                self.__restartEffectData(exposedVehicleData, effect, isSource=False)
            else:
                noneArgs = effect.args(None, None, None, None, None, None, None)
                if isAttachedVehicle:
                    self.sessionProvider.invalidateVehicleState(effect.vehicleViewState, noneArgs._asdict())
                else:
                    ctrl = self.sessionProvider.shared.feedback
                    if ctrl is not None:
                        ctrl.invalidateBuffEffect(effect.feedbackEventID, vehicleID, noneArgs._asdict())
        return

    def __restartEffectData(self, effectData, effect, isSource=False, atPeriod=None):
        if effectData is not None:
            effectData.cancelCallback()
            currentPeriod = atPeriod if atPeriod is not None else max(effectData.getNextPeriodAndStartTime(BigWorld.serverTime())[0] - 1, EffectData.EFFECT_PERIOD.EXPOSED)
            if isSource:
                self.__evaluateEffectSourceData(effectData, currentPeriod, effect)
            else:
                self.__evaluateExposedData(effectData, currentPeriod, effect)
        return

    def __getMotor(self, vehicleId):
        vehicle = BigWorld.entity(vehicleId)
        return None if not vehicle else BigWorld.Servo(makeVehicleEntityMP(vehicle))

    def __onSmokeScreenUpdated(self, args):
        for key, value in args.iteritems():
            if value is not None:
                smokeItem = self.__smokeScreen.get(key, None)
                if smokeItem is not None:
                    LOG_ERROR_DEV('Smoke Item is not none! Needs to be deleted or updated ', key, value)
                else:
                    smokeItem = SmokeScreen(key, value)
                    self.__smokeScreen[key] = smokeItem
            self.__smokeScreen[key].stop()
            self.__smokeScreen[key] = None

        return
