# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/banner/birthday_banner_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class StatusEnum(Enum):
    ACTIVE = 'active'
    ENDING = 'ending'
    DISABLED = 'disabled'


class BirthdayBannerViewModel(ViewModel):
    __slots__ = ('toBirthdayEvent',)

    def __init__(self, properties=3, commands=1):
        super(BirthdayBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getIsAloneBanner(self):
        return self._getBool(0)

    def setIsAloneBanner(self, value):
        self._setBool(0, value)

    def getTimer(self):
        return self._getNumber(1)

    def setTimer(self, value):
        self._setNumber(1, value)

    def getStatus(self):
        return StatusEnum(self._getString(2))

    def setStatus(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(BirthdayBannerViewModel, self)._initialize()
        self._addBoolProperty('isAloneBanner', False)
        self._addNumberProperty('timer', 123456789)
        self._addStringProperty('status', StatusEnum.ACTIVE.value)
        self.toBirthdayEvent = self._addCommand('toBirthdayEvent')
