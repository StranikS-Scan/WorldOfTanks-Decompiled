# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/premium_quests_model.py
from frameworks.wulf import ViewModel

class PremiumQuestsModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(PremiumQuestsModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getCompletedMissionsCount(self):
        return self._getNumber(1)

    def setCompletedMissionsCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PremiumQuestsModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('completedMissionsCount', -1)
        self.onClick = self._addCommand('onClick')
