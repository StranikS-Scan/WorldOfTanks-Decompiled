# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/common/congratulations_window_view_model.py
from frameworks.wulf import ViewModel

class CongratulationsWindowViewModel(ViewModel):
    __slots__ = ('onClose', 'onLoaded')

    def __init__(self, properties=4, commands=2):
        super(CongratulationsWindowViewModel, self).__init__(properties=properties, commands=commands)

    def getIsCloseVisible(self):
        return self._getBool(0)

    def setIsCloseVisible(self, value):
        self._setBool(0, value)

    def getIsOnboarding(self):
        return self._getBool(1)

    def setIsOnboarding(self, value):
        self._setBool(1, value)

    def getMedalName(self):
        return self._getString(2)

    def setMedalName(self, value):
        self._setString(2, value)

    def getMissionId(self):
        return self._getNumber(3)

    def setMissionId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(CongratulationsWindowViewModel, self)._initialize()
        self._addBoolProperty('isCloseVisible', False)
        self._addBoolProperty('isOnboarding', False)
        self._addStringProperty('medalName', '')
        self._addNumberProperty('missionId', 0)
        self.onClose = self._addCommand('onClose')
        self.onLoaded = self._addCommand('onLoaded')
