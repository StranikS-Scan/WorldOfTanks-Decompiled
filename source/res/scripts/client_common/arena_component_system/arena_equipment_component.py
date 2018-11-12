# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/arena_equipment_component.py
from collections import namedtuple
from functools import partial
import BigWorld
import ResMgr
import Event
from vehicle_systems.components.terrain_circle_component import readTerrainCircleSettings
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS
from debug_utils import LOG_ERROR_DEV, LOG_ERROR
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.matrix_factory import makeVehicleEntityMP
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
from smoke_screen import SmokeScreen

def readInspireVisualSettings():
    xmlTag = 'InspireAreaVisual'
    filePath = 'scripts/dynamic_objects.xml'
    xmlSection = ResMgr.openSection(filePath)
    if xmlSection is None:
        LOG_ERROR("initSettings: Could not open section '{}' in file {}".format(xmlTag, filePath))
        return
    else:
        xmlCtx = (None, filePath)
        return readTerrainCircleSettings(xmlSection, xmlCtx, xmlTag)


g_inspireVisualSettings = readInspireVisualSettings()

class InspireData(object):

    class INSPIRE_PERIOD(CONST_CONTAINER):
        INSPIRED = 0
        INACTIVATION = 1
        OVER = 2

    TimerTuple = namedtuple('TimerTuple', ('period', 'callbackID'))

    def __init__(self, vehicleID, startTime, endTime, inactivationStartTime=None, inactivationEndTime=None):
        self.vehicleID = vehicleID
        self.startTime = startTime
        self.endTime = endTime
        self.inactivationStartTime = inactivationStartTime
        self.inactivationEndTime = inactivationEndTime
        self.__timerTuple = None
        return

    def updateTerrainCircle(self, radius):
        vehicle = BigWorld.entities.get(self.vehicleID)
        if vehicle is not None:
            vehicle.appearance.showTerrainCircle(radius, g_inspireVisualSettings)
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
        if vehicle is not None:
            vehicle.appearance.hideTerrainCircle()
        if self.__timerTuple is not None and self.__timerTuple.callbackID is not None:
            BigWorld.cancelCallback(self.__timerTuple.callbackID)
        self.__timerTuple = None
        return

    def getNextPeriodAndStartTime(self, currentTime, currentPeriod=None):
        periods = ((self.INSPIRE_PERIOD.INSPIRED, self.startTime), (self.INSPIRE_PERIOD.INACTIVATION, self.inactivationStartTime), (self.INSPIRE_PERIOD.OVER, self.inactivationEndTime))
        if currentPeriod is not None:
            nextPeriod = min(currentPeriod + 1, self.INSPIRE_PERIOD.OVER)
            return periods[nextPeriod]
        else:
            return next((period for period in periods if period[1] > currentTime), periods[self.INSPIRE_PERIOD.OVER])

    def __invokeCallback(self, func, period):
        self.__timerTuple = self.__timerTuple._replace(callbackID=None)
        func(self, period)
        return


InspireArgs = namedtuple('InspireArgs', ('isSourceVehicle', 'isInactivation', 'endTime', 'duration'))

class ArenaEquipmentComponent(ClientArenaComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.SMOKE, '', self.__onSmokeScreenUpdated)
        self.onSmokeScreenStarted = Event.Event(self._eventManager)
        self.onSmokeScreenEnded = Event.Event(self._eventManager)
        self.__smokeScreen = dict()
        self.__inspiredData = dict()
        self.__inspiringData = dict()

    def destroy(self):
        super(ArenaEquipmentComponent, self).destroy()
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.SMOKE, '', self.__onSmokeScreenUpdated)
        self.__smokeScreen.clear()
        SmokeScreen.enableSmokePostEffect(False)
        for inspireData in (data for data in self.__inspiredData.itervalues() if data is not None):
            inspireData.destroy()

        self.__inspiredData.clear()
        for inspiringData in (data for data in self.__inspiringData.itervalues() if data is not None):
            inspiringData.destroy()

        self.__inspiringData.clear()

    def removeInspire(self, vehicleId):
        needsRemove = False
        data = self.__inspiringData.pop(vehicleId, None)
        if data:
            needsRemove |= data.isActive
            data.destroy()
        data = self.__inspiredData.pop(vehicleId, None)
        if data:
            needsRemove |= data.isActive
            data.destroy()
        if needsRemove:
            noneArgs = InspireArgs(None, None, None, None)
            attachedVehicle = BigWorld.player().getVehicleAttached()
            isAttachedVehicle = attachedVehicle and vehicleId == attachedVehicle.id
            if isAttachedVehicle:
                self.sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.INSPIRE, noneArgs._asdict())
            else:
                ctrl = self.sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateInspire(vehicleId, noneArgs._asdict())
        return

    def updateInspired(self, vehicleID, startTime, endTime, inactivationStartTime, inactivationEndTime):
        inspiredData = self.__inspiredData.get(vehicleID, None)
        if startTime is None:
            if inspiredData is not None:
                inspiredData.startTime = inspiredData.endTime = inspiredData.inactivationStartTime = inspiredData.inactivationEndTime = 0
                inspiringData = self.__inspiringData.get(vehicleID, None)
                if inspiringData is not None:
                    inspiredData.destroy()
                    del self.__inspiredData[vehicleID]
                else:
                    self.__restartInspireData(inspiredData, isSource=False, atPeriod=InspireData.INSPIRE_PERIOD.OVER)
            return
        else:
            if inspiredData is None:
                self.__inspiredData[vehicleID] = inspiredData = InspireData(vehicleID, startTime, endTime, inactivationStartTime, inactivationEndTime)
            else:
                inspiredData.startTime = startTime
                inspiredData.endTime = endTime
                inspiredData.inactivationStartTime = inactivationStartTime
                inspiredData.inactivationEndTime = inactivationEndTime
            self.__restartInspireData(inspiredData, isSource=False)
            return

    def updateInspiringSource(self, vehicleID, startTime, endTime, inactivationDelay, inspireSourceRadius):
        inspiringData = self.__inspiringData.get(vehicleID, None)
        if startTime is None:
            if inspiringData is not None:
                inspiringData.startTime = inspiringData.endTime = inspiringData.inactivationStartTime = inspiringData.inactivationEndTime = 0
                self.__restartInspireData(inspiringData, isSource=True, atPeriod=InspireData.INSPIRE_PERIOD.OVER)
            return
        else:
            inspiredData = self.__inspiredData.get(vehicleID, None)
            if inspiredData is not None:
                inspiredData.cancelCallback()
            if inspiringData is None:
                self.__inspiringData[vehicleID] = inspiringData = InspireData(vehicleID=vehicleID, startTime=startTime, endTime=endTime, inactivationStartTime=endTime, inactivationEndTime=endTime + inactivationDelay if endTime is not None else None)
            else:
                inspiringData.startTime = startTime
                inspiringData.endTime = endTime
                inspiringData.inactivationStartTime = endTime
                inspiringData.inactivationEndTime = endTime + inactivationDelay if endTime is not None else None
            self.__restartInspireData(inspiringData, isSource=True, inspireSourceRadius=inspireSourceRadius)
            return

    def __evaluateInspiredData(self, data, period):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        vehicleID = data.vehicleID
        isAttachedVehicle = attachedVehicle and vehicleID == attachedVehicle.id
        isSourceVehicle = self.__inspiringData.get(vehicleID, None) is not None
        args = None
        if period == InspireData.INSPIRE_PERIOD.INSPIRED:
            if not isSourceVehicle:
                args = InspireArgs(False, False, data.endTime, data.endTime - data.startTime)
                data.setNextCallback(self.__evaluateInspiredData)
        elif period == InspireData.INSPIRE_PERIOD.INACTIVATION:
            args = InspireArgs(False, True, data.inactivationEndTime, data.inactivationEndTime - data.inactivationStartTime)
            data.setNextCallback(self.__evaluateInspiredData)
        else:
            args = InspireArgs(None, None, None, None)
            data.destroy()
            del self.__inspiredData[data.vehicleID]
        if args:
            if isAttachedVehicle:
                self.sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.INSPIRE, args._asdict())
            else:
                ctrl = self.sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateInspire(vehicleID, args._asdict())
        return

    def __evaluateInspiringSourceData(self, inspireSourceRadius, data, period):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        vehicleID = data.vehicleID
        isAttachedVehicle = attachedVehicle and vehicleID == attachedVehicle.id
        if period == InspireData.INSPIRE_PERIOD.INSPIRED:
            args = InspireArgs(True, False, data.endTime, data.endTime - data.startTime)
            if isAttachedVehicle:
                self.sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.INSPIRE, args._asdict())
            else:
                ctrl = self.sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateInspire(vehicleID, args._asdict())
            arenaDP = self.sessionProvider.getArenaDP()
            if arenaDP and arenaDP.isAllyTeam(arenaDP.getVehicleInfo(vehicleID).team):
                data.updateTerrainCircle(inspireSourceRadius)
            data.setNextCallback(partial(self.__evaluateInspiringSourceData, inspireSourceRadius))
        else:
            data.destroy()
            del self.__inspiringData[vehicleID]
            inspiredData = self.__inspiredData.get(vehicleID, None)
            if inspiredData is not None:
                self.__restartInspireData(inspiredData, isSource=False)
            else:
                noneArgs = InspireArgs(None, None, None, None)
                if isAttachedVehicle:
                    self.sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.INSPIRE, noneArgs._asdict())
                else:
                    ctrl = self.sessionProvider.shared.feedback
                    if ctrl is not None:
                        ctrl.invalidateInspire(vehicleID, noneArgs._asdict())
        return

    def __restartInspireData(self, inspireData, isSource=False, inspireSourceRadius=0, atPeriod=None):
        if inspireData is not None:
            inspireData.cancelCallback()
            currentPeriod = atPeriod if atPeriod is not None else max(inspireData.getNextPeriodAndStartTime(BigWorld.serverTime())[0] - 1, InspireData.INSPIRE_PERIOD.INSPIRED)
            if isSource:
                self.__evaluateInspiringSourceData(inspireSourceRadius, inspireData, currentPeriod)
            else:
                self.__evaluateInspiredData(inspireData, currentPeriod)
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
