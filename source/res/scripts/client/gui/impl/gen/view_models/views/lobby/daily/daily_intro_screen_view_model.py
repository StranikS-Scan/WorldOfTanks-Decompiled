# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_intro_screen_view_model.py
from frameworks.wulf import ViewModel

class DailyIntroScreenViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(DailyIntroScreenViewModel, self).__init__(properties=properties, commands=commands)

    def getIsPlayStreakEnabled(self):
        return self._getBool(0)

    def setIsPlayStreakEnabled(self, value):
        self._setBool(0, value)

    def getIsDailyQuestsEnabled(self):
        return self._getBool(1)

    def setIsDailyQuestsEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(DailyIntroScreenViewModel, self)._initialize()
        self._addBoolProperty('isPlayStreakEnabled', False)
        self._addBoolProperty('isDailyQuestsEnabled', False)
        self.onClose = self._addCommand('onClose')
