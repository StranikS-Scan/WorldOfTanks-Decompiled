# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/ny_quests_tab_view_model.py
from frameworks.wulf import ViewModel

class NyQuestsTabViewModel(ViewModel):
    __slots__ = ('onFinishAnimation',)

    def __init__(self, properties=2, commands=1):
        super(NyQuestsTabViewModel, self).__init__(properties=properties, commands=commands)

    def getIsBlocked(self):
        return self._getBool(0)

    def setIsBlocked(self, value):
        self._setBool(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NyQuestsTabViewModel, self)._initialize()
        self._addBoolProperty('isBlocked', False)
        self._addBoolProperty('isCompleted', False)
        self.onFinishAnimation = self._addCommand('onFinishAnimation')
