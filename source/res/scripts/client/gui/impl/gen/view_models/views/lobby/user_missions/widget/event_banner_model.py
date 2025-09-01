# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/event_banner_model.py
from frameworks.wulf import ViewModel

class EventBannerModel(ViewModel):
    __slots__ = ()
    APPEAR_PENDING = 'pending'
    APPEAR_READY_TO_PLAY = 'readyToPlay'
    APPEAR_NONE = 'none'
    BG_SIZE_BIG = 'big'
    BG_SIZE_MEDIUM = 'medium'
    BG_SIZE_SMALL = 'small'

    def __init__(self, properties=11, commands=0):
        super(EventBannerModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getBorderColor(self):
        return self._getString(1)

    def setBorderColor(self, value):
        self._setString(1, value)

    def getIntroDescription(self):
        return self._getString(2)

    def setIntroDescription(self, value):
        self._setString(2, value)

    def getInProgressDescription(self):
        return self._getString(3)

    def setInProgressDescription(self, value):
        self._setString(3, value)

    def getIsMode(self):
        return self._getBool(4)

    def setIsMode(self, value):
        self._setBool(4, value)

    def getBannerState(self):
        return self._getString(5)

    def setBannerState(self, value):
        self._setString(5, value)

    def getTimerValue(self):
        return self._getNumber(6)

    def setTimerValue(self, value):
        self._setNumber(6, value)

    def getEventStartDate(self):
        return self._getNumber(7)

    def setEventStartDate(self, value):
        self._setNumber(7, value)

    def getEventEndDate(self):
        return self._getNumber(8)

    def setEventEndDate(self, value):
        self._setNumber(8, value)

    def getAppearAnimationState(self):
        return self._getString(9)

    def setAppearAnimationState(self, value):
        self._setString(9, value)

    def getShowTimerBeforeEventEnd(self):
        return self._getNumber(10)

    def setShowTimerBeforeEventEnd(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(EventBannerModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('borderColor', '')
        self._addStringProperty('introDescription', '')
        self._addStringProperty('inProgressDescription', '')
        self._addBoolProperty('isMode', False)
        self._addStringProperty('bannerState', '')
        self._addNumberProperty('timerValue', 0)
        self._addNumberProperty('eventStartDate', 0)
        self._addNumberProperty('eventEndDate', 0)
        self._addStringProperty('appearAnimationState', '')
        self._addNumberProperty('showTimerBeforeEventEnd', 0)
