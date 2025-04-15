# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/play_streak/rewards_calendar_item.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class RewardsCalendarItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RewardsCalendarItem, self).__init__(properties=properties, commands=commands)

    def getDay(self):
        return self._getNumber(0)

    def setDay(self, value):
        self._setNumber(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def getTags(self):
        return self._getArray(2)

    def setTags(self, value):
        self._setArray(2, value)

    @staticmethod
    def getTagsType():
        return unicode

    def getAdditionalInfo(self):
        return self._getArray(3)

    def setAdditionalInfo(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAdditionalInfoType():
        return unicode

    def _initialize(self):
        super(RewardsCalendarItem, self)._initialize()
        self._addNumberProperty('day', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('tags', Array())
        self._addArrayProperty('additionalInfo', Array())
