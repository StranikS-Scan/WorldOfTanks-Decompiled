# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/overtime_component.py
import BigWorld
from client_arena_component_system import ClientArenaComponent
from constants import ARENA_SYNC_OBJECTS
import Event
from helpers.CallbackDelayer import CallbackDelayer

class OvertimeComponent(ClientArenaComponent, CallbackDelayer):
    duration = property(lambda self: self.__duration)
    endTime = property(lambda self: self.__endTime)
    isActive = property(lambda self: self.__isActive)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        CallbackDelayer.__init__(self)
        self.__duration = None
        self.__endTime = None
        self.__isActive = False
        self.__cbId = None
        self.onOvertimeStart = Event.Event(self._eventManager)
        self.onOvertimeOver = Event.Event(self._eventManager)
        return

    def activate(self):
        super(OvertimeComponent, self).activate()
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.OVERTIME, 'duration', self.__onDurationUpdated)
        self.addSyncDataCallback(ARENA_SYNC_OBJECTS.OVERTIME, 'endTime', self.__onEndTimeUpdated)

    def deactivate(self):
        super(OvertimeComponent, self).deactivate()
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.OVERTIME, 'duration', self.__onDurationUpdated)
        self.removeSyncDataCallback(ARENA_SYNC_OBJECTS.OVERTIME, 'endTime', self.__onEndTimeUpdated)

    def destroy(self):
        ClientArenaComponent.destroy(self)
        CallbackDelayer.destroy(self)

    def __onDurationUpdated(self, duration):
        self.__duration = duration
        self.__onDataChanged()

    def __onEndTimeUpdated(self, endTime):
        self.__endTime = endTime
        self.__onDataChanged()

    def __onDataChanged(self):
        currentTime = BigWorld.serverTime()
        if self.__isActive:
            if self.__duration is None or self.__endTime is None or currentTime >= self.__endTime or currentTime < self.__endTime - self.__duration:
                self.stopCallback(self.__startOvertime)
                self.__endOvertime()
            else:
                self.delayCallback(self.__endTime - currentTime, self.__endOvertime)
        elif self.__duration is not None and self.__endTime is not None:
            if self.__endTime - self.__duration <= currentTime < self.__endTime:
                self.stopCallback(self.__startOvertime)
                self.__startOvertime()
            else:
                self.delayCallback(self.__endTime - self.__duration - currentTime, self.__startOvertime)
        return

    def __startOvertime(self):
        self.__cbId = None
        self.__isActive = True
        self.onOvertimeStart(self.__endTime)
        return

    def __endOvertime(self):
        self.__cbId = None
        self.__isActive = False
        self.onOvertimeOver()
        return
