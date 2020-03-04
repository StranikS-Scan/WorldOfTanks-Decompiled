# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_entry_point_view_model.py
from frameworks.wulf import ViewModel

class BattlePassEntryPointViewModel(ViewModel):
    __slots__ = ('onClick',)
    STATE_DISABLED = 'disabled'
    STATE_SEASON_WAITING = 'seasonWaiting'
    STATE_NORMAL = 'normal'

    def __init__(self, properties=9, commands=1):
        super(BattlePassEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getPrevProgression(self):
        return self._getReal(1)

    def setPrevProgression(self, value):
        self._setReal(1, value)

    def getProgression(self):
        return self._getReal(2)

    def setProgression(self, value):
        self._setReal(2, value)

    def getIsPostProgression(self):
        return self._getBool(3)

    def setIsPostProgression(self, value):
        self._setBool(3, value)

    def getHasBattlePass(self):
        return self._getBool(4)

    def setHasBattlePass(self, value):
        self._setBool(4, value)

    def getIsPostProgressionCompleted(self):
        return self._getBool(5)

    def setIsPostProgressionCompleted(self, value):
        self._setBool(5, value)

    def getState(self):
        return self._getString(6)

    def setState(self, value):
        self._setString(6, value)

    def getIsSmall(self):
        return self._getBool(7)

    def setIsSmall(self, value):
        self._setBool(7, value)

    def getTooltipID(self):
        return self._getNumber(8)

    def setTooltipID(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(BattlePassEntryPointViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addRealProperty('prevProgression', 0.0)
        self._addRealProperty('progression', -1)
        self._addBoolProperty('isPostProgression', False)
        self._addBoolProperty('hasBattlePass', False)
        self._addBoolProperty('isPostProgressionCompleted', False)
        self._addStringProperty('state', '')
        self._addBoolProperty('isSmall', False)
        self._addNumberProperty('tooltipID', 0)
        self.onClick = self._addCommand('onClick')
