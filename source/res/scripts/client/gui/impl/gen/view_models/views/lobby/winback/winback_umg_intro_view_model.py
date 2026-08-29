# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/winback_umg_intro_view_model.py
from frameworks.wulf import ViewModel

class WinbackUmgIntroViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(WinbackUmgIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getHasBattlePass(self):
        return self._getBool(0)

    def setHasBattlePass(self, value):
        self._setBool(0, value)

    def getBackgroundPlugin(self):
        return self._getString(1)

    def setBackgroundPlugin(self, value):
        self._setString(1, value)

    def getDailyQuestsPlugin(self):
        return self._getString(2)

    def setDailyQuestsPlugin(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(WinbackUmgIntroViewModel, self)._initialize()
        self._addBoolProperty('hasBattlePass', False)
        self._addStringProperty('backgroundPlugin', '')
        self._addStringProperty('dailyQuestsPlugin', '')
        self.onClose = self._addCommand('onClose')
