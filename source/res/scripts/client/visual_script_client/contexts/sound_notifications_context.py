# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/contexts/sound_notifications_context.py
import weakref
import BigWorld
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.context import VScriptContext, vse_event_out, vse_func_call

class SoundNotificationsContext(VScriptContext):

    def __init__(self):
        VScriptContext.__init__(self, ASPECT.CLIENT)
        avatar = BigWorld.player()
        if avatar:
            self.__soundNotifications = avatar.soundNotifications
            if self.__soundNotifications:
                self.__soundNotifications.onPlayEvent += self.onPlayQueueEvent
                self.__soundNotifications.onAddEvent += self.onAddQueueEvent

    def destroy(self):
        if self.__soundNotifications:
            self.__soundNotifications.onPlayEvent -= self.onPlayQueueEvent
            self.__soundNotifications.onAddEvent -= self.onAddQueueEvent
            self.__soundNotifications = None
        return

    @vse_event_out(SLOT_TYPE.STR, display_name='OnPlayQueueEvent', description='Reacts on gameplay event triggered from queue', aspects=[ASPECT.CLIENT])
    def onPlayQueueEvent(self, eventName):
        pass

    @vse_event_out(SLOT_TYPE.STR, display_name='OnAddQueueEvent', description='Reacts on gameplay event added to queue', aspects=[ASPECT.CLIENT])
    def onAddQueueEvent(self, eventName):
        pass

    @vse_func_call(None, (SLOT_TYPE.INT,), display_name='PlayNextQueueEvent', description='Triggers next queue Event by queue number', aspects=[ASPECT.CLIENT])
    def playNextQueueEvent(self, queueNum):
        if self.__soundNotifications:
            self.__soundNotifications.playNextQueueEvent(queueNum)

    @vse_func_call(None, (SLOT_TYPE.INT, SLOT_TYPE.INT), display_name='ReplayLastQueueEvent', description='Triggers next soundEvent of current eventChain', aspects=[ASPECT.CLIENT])
    def replayLastQueueEvent(self, queueNum):
        if self.__soundNotifications:
            self.__soundNotifications.replayLastQueueEvent(queueNum)

    @vse_func_call(SLOT_TYPE.STR, (SLOT_TYPE.INT,), display_name='GetFirstQueueEvent', description='Returns name of first Event in queue if exists', aspects=[ASPECT.CLIENT])
    def getFirstQueueEvent(self, queueNum):
        eventName = ''
        if self.__soundNotifications:
            eventName = self.__soundNotifications.getFirstQueueEvent(queueNum)
        return eventName

    @vse_func_call(None, (SLOT_TYPE.INT,), display_name='ClearQueue', description='Clears queue by queue Number', aspects=[ASPECT.CLIENT])
    def clearQueue(self, queueNum):
        if self.__soundNotifications:
            self.__soundNotifications.clearQueue(queueNum)

    @vse_func_call(SLOT_TYPE.BOOL, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetEventInfoBool', description='Returns Event info from sound_notifications.xml by eventName', aspects=[ASPECT.CLIENT])
    def getEventInfoBool(self, eventName, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getEventInfo(eventName, parameter)
        return value.lower() in ('1', 'true')

    @vse_func_call(SLOT_TYPE.INT, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetEventInfoInt', description='Returns Event info from sound_notifications.xml by eventName', aspects=[ASPECT.CLIENT])
    def getEventInfoInt(self, eventName, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getEventInfo(eventName, parameter)
        return int(value) if value else 0

    @vse_func_call(SLOT_TYPE.FLOAT, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetEventInfoFloat', description='Returns Event info from sound_notifications.xml by eventName', aspects=[ASPECT.CLIENT])
    def getEventInfoFloat(self, eventName, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getEventInfo(eventName, parameter)
        return float(value) if value else 0.0

    @vse_func_call(SLOT_TYPE.STR, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetEventInfoString', description='Returns Event info from sound_notifications.xml by eventName', aspects=[ASPECT.CLIENT])
    def getEventInfoString(self, eventName, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getEventInfo(eventName, parameter)
        return value

    @vse_func_call(arrayOf(SLOT_TYPE.STR), (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetEventInfoStringArray', description='Returns Event info from sound_notifications.xml by eventName', aspects=[ASPECT.CLIENT])
    def getEventInfoStringArray(self, eventName, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getEventInfo(eventName, parameter)
        return value.split()

    @vse_func_call(SLOT_TYPE.BOOL, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetCircumstanceInfoBool', description='Returns Circumstance info from sound_circumstances.xml by Circumstance index', aspects=[ASPECT.CLIENT])
    def getCircumstanceInfoBool(self, circIndex, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getCircumstanceInfo(circIndex, parameter)
        return value.lower() in ('1', 'true')

    @vse_func_call(SLOT_TYPE.INT, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetCircumstanceInfoInt', description='Returns Circumstance info from sound_circumstances.xml by Circumstance index', aspects=[ASPECT.CLIENT])
    def getCircumstanceInfoInt(self, circIndex, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getCircumstanceInfo(circIndex, parameter)
        return int(value) if value else 0

    @vse_func_call(SLOT_TYPE.STR, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetCircumstanceInfoString', description='Returns Circumstance info from sound_circumstances.xml by Circumstance index', aspects=[ASPECT.CLIENT])
    def getCircumstanceInfoString(self, circIndex, parameter):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getCircumstanceInfo(circIndex, parameter)
        return value

    @vse_func_call(SLOT_TYPE.STR, (SLOT_TYPE.INT,), display_name='GetPlayingEventName', description='Returns Name of playing Event', aspects=[ASPECT.CLIENT])
    def getPlayingEventName(self, queueNum):
        value = None
        if self.__soundNotifications:
            value = self.__soundNotifications.getPlayingEventData(queueNum, 'eventName')
        return value

    @vse_func_call(SLOT_TYPE.VEHICLE, (SLOT_TYPE.INT,), display_name='GetPlayingEventVehicle', description='Returns Vehicle of playing Event', aspects=[ASPECT.CLIENT])
    def getPlayingEventVehicle(self, queueNum):
        value = None
        if self.__soundNotifications:
            value = self.__soundNotifications.getPlayingEventData(queueNum, 'vehicle')
        return weakref.proxy(value) if value else None

    @vse_func_call(SLOT_TYPE.VEHICLE, (SLOT_TYPE.INT,), display_name='GetPlayingEventBoundVehicle', description='Returns BoundVehicle of playing Event', aspects=[ASPECT.CLIENT])
    def getPlayingEventBoundVehicle(self, queueNum):
        value = None
        if self.__soundNotifications:
            value = self.__soundNotifications.getPlayingEventData(queueNum, 'boundVehicle')
        return weakref.proxy(value) if value else None

    @vse_func_call(SLOT_TYPE.VECTOR3, (SLOT_TYPE.INT,), display_name='GetPlayingEventPosition', description='Returns Position of playing Event', aspects=[ASPECT.CLIENT])
    def getPlayingEventPosition(self, queueNum):
        value = None
        if self.__soundNotifications:
            value = self.__soundNotifications.getPlayingEventData(queueNum, 'position')
        return value

    @vse_func_call(SLOT_TYPE.BOOL, (SLOT_TYPE.INT,), display_name='GetPlayingEventIs2D', description='Returns is playing Event 2D', aspects=[ASPECT.CLIENT])
    def getPlayingEventIs2D(self, queueNum):
        value = None
        if self.__soundNotifications:
            value = self.__soundNotifications.getPlayingEventData(queueNum, 'is2D')
        return value

    @vse_func_call(SLOT_TYPE.STR, (SLOT_TYPE.STR, SLOT_TYPE.STR), display_name='GetCircumstanceIndex', description='Returns Circumstance Index from sound_circumstances.xml by Circumstance group and name', aspects=[ASPECT.CLIENT])
    def getCircumstanceIndex(self, circGroup, circName):
        value = ''
        if self.__soundNotifications:
            value = self.__soundNotifications.getCircumstanceIndex(circGroup, circName)
        return value

    @vse_func_call(None, (SLOT_TYPE.STR, SLOT_TYPE.FLOAT), display_name='SetEventCooldown', description='Sets Cooldown time for Event by eventName', aspects=[ASPECT.CLIENT])
    def setEventCooldown(self, eventName, cooldown):
        if self.__soundNotifications:
            self.__soundNotifications.setEventCooldown(eventName, cooldown)

    @vse_func_call(None, (SLOT_TYPE.STR, SLOT_TYPE.INT, SLOT_TYPE.FLOAT), display_name='SetEventPriority', description='Sets temporary Priority for Event by eventName', aspects=[ASPECT.CLIENT])
    def setEventPriority(self, eventName, priority, hold):
        if self.__soundNotifications:
            self.__soundNotifications.setEventPriority(eventName, priority, hold)

    @vse_func_call(None, (SLOT_TYPE.STR, SLOT_TYPE.INT, SLOT_TYPE.FLOAT), display_name='SetCircumstanceWeight', description='Sets temporary Weight for circumstance', aspects=[ASPECT.CLIENT])
    def setCircumstanceWeight(self, circIndex, weight, hold):
        if self.__soundNotifications:
            self.__soundNotifications.setCircumstanceWeight(circIndex, weight, hold)

    @vse_func_call(None, (SLOT_TYPE.STR, SLOT_TYPE.INT, SLOT_TYPE.FLOAT), display_name='SetCircumstanceGroupWeight', description='Sets temporary Weight for group of circumstances', aspects=[ASPECT.CLIENT])
    def setCircumstanceGroupWeight(self, groupName, weight, hold):
        if self.__soundNotifications:
            self.__soundNotifications.setCircumstanceGroupWeight(groupName, weight, hold)
