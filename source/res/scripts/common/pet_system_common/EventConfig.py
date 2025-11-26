# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pet_system_common/EventConfig.py
import typing
from pet_constants import PetEventsConsts as pc, PetEventTypeConsts as eventTypes
if typing.TYPE_CHECKING:
    from typing import Dict

class EventConfig(object):

    def __init__(self, config):
        self._config = config

    def getEvents(self):
        return self._config

    def getEventById(self, eventID):
        return self._config.get(eventID, {})

    def getEventType(self, eventID):
        return self.getEventById(eventID).get(pc.EVENT_TYPE, eventTypes.BASIC)

    def getEventRewardID(self, eventID):
        return self.getEventById(eventID).get(pc.EVENT_REWARD, 0)
