# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quest_reroll_view_model.py
from frameworks.wulf import ViewModel

class DailyQuestRerollViewModel(ViewModel):
    __slots__ = ('onClose', 'onReroll')

    def __init__(self, properties=3, commands=2):
        super(DailyQuestRerollViewModel, self).__init__(properties=properties, commands=commands)

    def getIsAlert(self):
        return self._getBool(0)

    def setIsAlert(self, value):
        self._setBool(0, value)

    def getRerollCooldown(self):
        return self._getNumber(1)

    def setRerollCooldown(self, value):
        self._setNumber(1, value)

    def getIsPremium(self):
        return self._getBool(2)

    def setIsPremium(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(DailyQuestRerollViewModel, self)._initialize()
        self._addBoolProperty('isAlert', False)
        self._addNumberProperty('rerollCooldown', 0)
        self._addBoolProperty('isPremium', False)
        self.onClose = self._addCommand('onClose')
        self.onReroll = self._addCommand('onReroll')
