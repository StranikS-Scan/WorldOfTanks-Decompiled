# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/battle/prebattle_window_view_model.py
from frameworks.wulf import ViewModel

class PrebattleWindowViewModel(ViewModel):
    __slots__ = ('onGotoBattle', 'onLoaded')

    def __init__(self, properties=2, commands=2):
        super(PrebattleWindowViewModel, self).__init__(properties=properties, commands=commands)

    def getIsLoading(self):
        return self._getBool(0)

    def setIsLoading(self, value):
        self._setBool(0, value)

    def getMissionNumber(self):
        return self._getNumber(1)

    def setMissionNumber(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PrebattleWindowViewModel, self)._initialize()
        self._addBoolProperty('isLoading', False)
        self._addNumberProperty('missionNumber', 0)
        self.onGotoBattle = self._addCommand('onGotoBattle')
        self.onLoaded = self._addCommand('onLoaded')
