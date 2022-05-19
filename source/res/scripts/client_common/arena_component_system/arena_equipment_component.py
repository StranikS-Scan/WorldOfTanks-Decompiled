# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/arena_equipment_component.py
from collections import namedtuple
from functools import partial
import logging
import BigWorld
from aih_constants import CTRL_MODE_NAME
from battle_royale.gui.constants import BattleRoyaleEquipments
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS, ARENA_GUI_TYPE
from debug_utils import LOG_ERROR_DEV
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from gui.battle_control.matrix_factory import makeVehicleEntityMP
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles
from shared_utils import CONST_CONTAINER
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from smoke_screen import SmokeScreen
from AffectComponent import RepairAffectComponent, TrapAffectComponent, FireCircleAffectComponent
_logger = logging.getLogger(__name__)
_EQUIPMENT_AFFECT_COMPONENTS = {BattleRoyaleEquipments.FIRE_CIRCLE: FireCircleAffectComponent,
 BattleRoyaleEquipments.TRAP_POINT: TrapAffectComponent}

class EffectData(object):

    class EFFECT_PERIOD(CONST_CONTAINER):
        EXPOSED = 0
        INACTIVATION = 1
        OVER = 2

    TimerTuple = namedtuple('TimerTuple', ('period', 'callbackID'))
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicleID, startTime, endTime, visualSettings, inactivationStartTime=None, inactivationEndTime=None, primary=True, radius=None, senderKey=None, equipmentID=None, inactivationSource=False):
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
        self.inactivationSource = inactivationSource
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

    def __new__(cls, isSourceVehicle, isInactivation, endTime, duration, _, senderKey, *__):
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


class ArenaEquipmentComponent(ClientArenaComponent, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        CallbackDelayer.__init__(self)
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
            arenaGuiType = BigWorld.player().arenaGuiType
            self.__inspiringEffect = Effect('inspire', InspireArgsAdapter, VEHICLE_VIEW_STATE.INSPIRE, FEEDBACK_EVENT_ID.VEHICLE_INSPIRE, dynamicObjects.getInspiringEffect())
            if arenaGuiType in (ARENA_GUI_TYPE.BATTLE_ROYALE, ARENA_GUI_TYPE.EPIC_BATTLE, ARENA_GUI_TYPE.EPIC_TRAINING):
                self.__healingEffect = Effect('healPoint', HealPointArgsAdapter, VEHICLE_VIEW_STATE.HEALING, FEEDBACK_EVENT_ID.VEHICLE_HEAL_POINT, dynamicObjects.getHealPointEffect())
            if arenaGuiType == ARENA_GUI_TYPE.BATTLE_ROYALE:
                self.__repairPointEffect = Effect('repairPoint', HealPointArgsAdapter, VEHICLE_VIEW_STATE.REPAIR_POINT, FEEDBACK_EVENT_ID.VEHICLE_REPAIR_POINT, dynamicObjects.getRepairPointEffect())
        self.__subscribe()
        return

    def deactivate(self):
        super(ArenaEquipmentComponent, self).deactivate()
        CallbackDelayer.destroy(self)
        self.__unsubscribe()
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.SMOKE, '', self.__onSmokeScreenUpdated)
        self.__smokeScreen.clear()
        if self.__inspiringEffect is not None:
            self.__inspiringEffect.destroy()
        if self.__healingEffect is not None:
            self.__healingEffect.destroy()
        if self.__repairPointEffect is not None:
            self.__repairPointEffect.destroy()
        return

    def __subscribe(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        aih = avatar_getter.getInputHandler()
        if aih is not None:
            aih.onCameraChanged += self.__onCameraChanged
        return

    def __unsubscribe(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        aih = avatar_getter.getInputHandler()
        if aih is not None:
            aih.onCameraChanged -= self.__onCameraChanged
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

    def __updateExposedToEffect(self, vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, primary, equipmentID, effect, isInfluenceZone, inactivationSource):
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
                effect.exposedVehicles[vehicleID] = exposedVehicleData = EffectData(vehicleID=vehicleID, startTime=startTime, endTime=endTime, visualSettings=effect.visualSettings, inactivationStartTime=inactivationStartTime, inactivationEndTime=inactivationEndTime, primary=primary, senderKey=senderKey, equipmentID=equipmentID, inactivationSource=inactivationSource)
            else:
                exposedVehicleData.startTime = startTime
                exposedVehicleData.endTime = endTime
                exposedVehicleData.inactivationStartTime = inactivationStartTime
                exposedVehicleData.inactivationEndTime = inactivationEndTime
                exposedVehicleData.senderKey = senderKey
                exposedVehicleData.equipmentID = equipmentID
                exposedVehicleData.inactivationSource = inactivationSource
            self.__checkAffectComponent(vehicleID, RepairAffectComponent, isInfluenceZone)
            self.__restartEffectData(exposedVehicleData, effect, isSource=False)
            return

    def __checkAffectComponent(self, vehicleID, affectComponent, isInfluenceZone):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle and vehicle.isAlive():
            appearance = vehicle.appearance
            if appearance.findComponentByType(affectComponent) is not None:
                if not isInfluenceZone:
                    curAffectComponent = appearance.findComponentByType(affectComponent)
                    appearance.removeComponent(curAffectComponent)
                    if curAffectComponent.hasDebuff:
                        vehicle.onDebuffEffectApplied(False)
                return
            if isInfluenceZone:
                appearance.createComponent(affectComponent, appearance.gameObject, vehicle.isPlayerVehicle, BigWorld.player().spaceID)
                curAffectComponent = appearance.findComponentByType(affectComponent)
                if curAffectComponent.hasDebuff:
                    vehicle.onDebuffEffectApplied(True)
        return

    def _updateEffectSource(self, vehicleID, startTime, endTime, inactivationDelay, effectSourceRadius, effect, equipmentID=None):
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
                effect.providingVehicles[vehicleID] = providingVehicleData = EffectData(vehicleID=vehicleID, startTime=startTime, endTime=endTime, visualSettings=effect.visualSettings, inactivationStartTime=endTime, inactivationEndTime=endTime + inactivationDelay if endTime is not None else None, radius=effectSourceRadius, equipmentID=equipmentID)
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

    def updateInspired(self, vehicleID, startTime, endTime, inactivationStartTime, inactivationEndTime, primary, equipmentID, inactivationSource):
        self.__updateExposedToEffect(vehicleID, None, startTime, endTime, inactivationStartTime, inactivationEndTime, primary, equipmentID, self.__inspiringEffect, False, inactivationSource)
        return

    def updateHealing(self, vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime):
        self.__updateExposedToEffect(vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, True, None, self.__healingEffect, False, False)
        return

    def updateHealOverTime(self, vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, isInfluenceZone):
        self.__updateExposedToEffect(vehicleID, senderKey, startTime, endTime, inactivationStartTime, inactivationEndTime, True, None, self.__repairPointEffect, isInfluenceZone, False)
        return

    def updateDebuff(self, vehicleID, equipmentID):
        if equipmentID > -1 and vehicles.g_cache.equipments()[equipmentID].name in _EQUIPMENT_AFFECT_COMPONENTS:
            affectComponent = _EQUIPMENT_AFFECT_COMPONENTS[vehicles.g_cache.equipments()[equipmentID].name]
            self.__checkAffectComponent(vehicleID, affectComponent, True)
        else:
            for affectComponent in _EQUIPMENT_AFFECT_COMPONENTS.values():
                self.__checkAffectComponent(vehicleID, affectComponent, False)

    def updateInspiringSource(self, vehicleID, startTime, endTime, inactivationDelay, inspireSourceRadius, equipmentID):
        self._updateEffectSource(vehicleID, startTime, endTime, inactivationDelay, inspireSourceRadius, self.__inspiringEffect, equipmentID)

    def updateHealingSource(self, vehicleID, startTime, endTime, inactivationDelay, healingSourceRadius):
        self._updateEffectSource(vehicleID, startTime, endTime, inactivationDelay, healingSourceRadius, self.__healingEffect)

    def __evaluateExposedData(self, data, period, effect):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        vehicleID = data.vehicleID
        isAttachedVehicle = attachedVehicle and vehicleID == attachedVehicle.id
        isSourceVehicle = effect.providingVehicles.get(vehicleID, None) is not None
        if effect.name == 'inspire':
            isSourceVehicle = data.inactivationSource
        if period == EffectData.EFFECT_PERIOD.EXPOSED:
            args = effect.args(isSourceVehicle, False, data.endTime, data.endTime - BigWorld.serverTime(), data.primary, data.senderKey, data.equipmentID)
            data.setNextCallback(partial(self.__evaluateExposedData, effect=effect))
        elif period == EffectData.EFFECT_PERIOD.INACTIVATION:
            args = effect.args(isSourceVehicle, True, data.inactivationEndTime, data.inactivationEndTime - data.inactivationStartTime, data.primary, data.senderKey, data.equipmentID)
            data.setNextCallback(partial(self.__evaluateExposedData, effect=effect))
        else:
            self.__checkAffectComponent(data.vehicleID, RepairAffectComponent, False)
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

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SMOKE:
            self.__updateSmokePostEffect()

    def __onCameraChanged(self, ctrlMode, _=None):
        self.__updateSmokePostEffect()

    def __updateSmokePostEffect(self):
        self.delayCallback(0.1, self.__doUpdateSmokePostEffect)

    @staticmethod
    def __doUpdateSmokePostEffect():
        aih = avatar_getter.getInputHandler()
        avatar = BigWorld.player()
        if avatar is None or aih is None or aih.ctrlModeName == CTRL_MODE_NAME.DEATH_FREE_CAM:
            SmokeScreen.enableSmokePostEffect(enabled=False)
        else:
            smokeInfo = avatar.lastSmokeInfo
            SmokeScreen.enableSmokePostEffect(enabled=bool(smokeInfo), smokeInfos=smokeInfo)
        return
