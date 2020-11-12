# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/cn_loot_boxes/china_loot_boxes_welcome_screen_model.py
from frameworks.wulf import ViewModel

class ChinaLootBoxesWelcomeScreenModel(ViewModel):
    __slots__ = ('onBuy', 'onClose')

    def __init__(self, properties=2, commands=2):
        super(ChinaLootBoxesWelcomeScreenModel, self).__init__(properties=properties, commands=commands)

    def getTimeLeft(self):
        return self._getNumber(0)

    def setTimeLeft(self, value):
        self._setNumber(0, value)

    def getDailyBoxesCount(self):
        return self._getNumber(1)

    def setDailyBoxesCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(ChinaLootBoxesWelcomeScreenModel, self)._initialize()
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('dailyBoxesCount', 30)
        self.onBuy = self._addCommand('onBuy')
        self.onClose = self._addCommand('onClose')
