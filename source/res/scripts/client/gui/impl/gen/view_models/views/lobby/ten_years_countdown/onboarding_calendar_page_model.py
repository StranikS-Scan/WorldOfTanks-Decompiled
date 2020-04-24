# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ten_years_countdown/onboarding_calendar_page_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.ten_years_countdown.onboarding_calendar_block_model import OnboardingCalendarBlockModel

class OnboardingCalendarPageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(OnboardingCalendarPageModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getBlocks(self):
        return self._getArray(1)

    def setBlocks(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(OnboardingCalendarPageModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('blocks', Array())
