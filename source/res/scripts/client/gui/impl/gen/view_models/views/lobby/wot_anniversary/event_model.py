# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/event_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EventType(Enum):
    INVOICE_PROCESSED = 'invoiceProcessed'
    INVOICE_REJECTED = 'invoiceRejected'
    REGULAR_REWARDS_RECEIVED = 'regularRewardsReceived'
    TURN_PAGE = 'turnPage'


class EventModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EventModel, self).__init__(properties=properties, commands=commands)

    def getEventType(self):
        return EventType(self._getString(0))

    def setEventType(self, value):
        self._setString(0, value.value)

    def getPayload(self):
        return self._getString(1)

    def setPayload(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(EventModel, self)._initialize()
        self._addStringProperty('eventType', EventType.INVOICE_PROCESSED.value)
        self._addStringProperty('payload', '')
