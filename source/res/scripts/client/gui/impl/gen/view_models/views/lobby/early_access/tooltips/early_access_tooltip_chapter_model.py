# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/tooltips/early_access_tooltip_chapter_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TooltipChapterState(Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    NOTAVAILABLE = 'notAvailable'
    POSTPROGRESSION = 'postProgression'
    LOCKED = 'locked'


class EarlyAccessTooltipChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(EarlyAccessTooltipChapterModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getState(self):
        return TooltipChapterState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getCompletedQuests(self):
        return self._getNumber(2)

    def setCompletedQuests(self, value):
        self._setNumber(2, value)

    def getTotalQuests(self):
        return self._getNumber(3)

    def setTotalQuests(self, value):
        self._setNumber(3, value)

    def getAnnouncementTimestamp(self):
        return self._getNumber(4)

    def setAnnouncementTimestamp(self, value):
        self._setNumber(4, value)

    def getLockedUntilQuestsComplete(self):
        return self._getNumber(5)

    def setLockedUntilQuestsComplete(self, value):
        self._setNumber(5, value)

    def getMinVehicleLvl(self):
        return self._getNumber(6)

    def setMinVehicleLvl(self, value):
        self._setNumber(6, value)

    def getMaxVehicleLvl(self):
        return self._getNumber(7)

    def setMaxVehicleLvl(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(EarlyAccessTooltipChapterModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('state')
        self._addNumberProperty('completedQuests', 0)
        self._addNumberProperty('totalQuests', 0)
        self._addNumberProperty('announcementTimestamp', 0)
        self._addNumberProperty('lockedUntilQuestsComplete', 0)
        self._addNumberProperty('minVehicleLvl', 0)
        self._addNumberProperty('maxVehicleLvl', 10)
