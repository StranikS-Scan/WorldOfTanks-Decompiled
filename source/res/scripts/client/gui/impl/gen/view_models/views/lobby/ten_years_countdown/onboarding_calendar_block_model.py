# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/onboarding_calendar_block_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class OnboardingCalendarBlockModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(OnboardingCalendarBlockModel, self).__init__(properties=properties, commands=commands)

    def getMonth(self):
        return self._getResource(0)

    def setMonth(self, value):
        self._setResource(0, value)

    def getBlockState(self):
        return self._getString(1)

    def setBlockState(self, value):
        self._setString(1, value)

    def getTitleNumber(self):
        return self._getResource(2)

    def setTitleNumber(self, value):
        self._setResource(2, value)

    def getTitle(self):
        return self._getResource(3)

    def setTitle(self, value):
        self._setResource(3, value)

    def getYears(self):
        return self._getResource(4)

    def setYears(self, value):
        self._setResource(4, value)

    def getDescription(self):
        return self._getResource(5)

    def setDescription(self, value):
        self._setResource(5, value)

    def getFeaturesTitle(self):
        return self._getResource(6)

    def setFeaturesTitle(self, value):
        self._setResource(6, value)

    def getFeatures(self):
        return self._getArray(7)

    def setFeatures(self, value):
        self._setArray(7, value)

    def _initialize(self):
        super(OnboardingCalendarBlockModel, self)._initialize()
        self._addResourceProperty('month', R.invalid())
        self._addStringProperty('blockState', '')
        self._addResourceProperty('titleNumber', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('years', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addResourceProperty('featuresTitle', R.invalid())
        self._addArrayProperty('features', Array())
