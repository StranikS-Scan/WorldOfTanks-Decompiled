# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/event_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EventStatus(Enum):
    DONE = 'done'
    UNDONESUBSCRIPTION = 'undoneSubscription'
    LOCKED = 'notAvailable'
    ACTIVE = ''


class EventModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(EventModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getGroupId(self):
        return self._getString(1)

    def setGroupId(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getNumber(2)

    def setType(self, value):
        self._setNumber(2, value)

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getDecoration(self):
        return self._getNumber(5)

    def setDecoration(self, value):
        self._setNumber(5, value)

    def getStatus(self):
        return EventStatus(self._getString(6))

    def setStatus(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(EventModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('groupId', '')
        self._addNumberProperty('type', 0)
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('decoration', 0)
        self._addStringProperty('status')
