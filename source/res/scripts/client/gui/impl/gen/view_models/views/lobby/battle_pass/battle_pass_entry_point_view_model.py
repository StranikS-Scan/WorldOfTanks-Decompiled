# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_entry_point_view_model.py
from frameworks.wulf import ViewModel

class BattlePassEntryPointViewModel(ViewModel):
    __slots__ = ('onClick',)
    STATE_DISABLED = 'disabled'
    STATE_SEASON_WAITING = 'seasonWaiting'
    STATE_NORMAL = 'normal'
    ANIM_STATE_NORMAL = 'normal'
    ANIM_STATE_SHOW_NEW_LEVEL = 'showNewLevel'
    ANIM_STATE_SHOW_BUY_BATTLEPASS = 'showBuyBP'
    ANIM_STATE_SHOW_ATTENTION = 'showAttention'
    ANIM_STATE_SHOW_POST_PROGRESSION_COMPLETED = 'showPostProgressionCompleted'
    ANIM_STATE_SHOW_SWITCH_TO_POST_PROGRESSION = 'showSwitchToPostProgression'

    def __init__(self, properties=14, commands=1):
        super(BattlePassEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getPrevLevel(self):
        return self._getNumber(0)

    def setPrevLevel(self, value):
        self._setNumber(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getMaxCommonLevel(self):
        return self._getNumber(2)

    def setMaxCommonLevel(self, value):
        self._setNumber(2, value)

    def getPrevProgression(self):
        return self._getReal(3)

    def setPrevProgression(self, value):
        self._setReal(3, value)

    def getProgression(self):
        return self._getReal(4)

    def setProgression(self, value):
        self._setReal(4, value)

    def getIsPostProgression(self):
        return self._getBool(5)

    def setIsPostProgression(self, value):
        self._setBool(5, value)

    def getHasBattlePass(self):
        return self._getBool(6)

    def setHasBattlePass(self, value):
        self._setBool(6, value)

    def getIsPostProgressionCompleted(self):
        return self._getBool(7)

    def setIsPostProgressionCompleted(self, value):
        self._setBool(7, value)

    def getState(self):
        return self._getString(8)

    def setState(self, value):
        self._setString(8, value)

    def getIsSmall(self):
        return self._getBool(9)

    def setIsSmall(self, value):
        self._setBool(9, value)

    def getTooltipID(self):
        return self._getNumber(10)

    def setTooltipID(self, value):
        self._setNumber(10, value)

    def getCanPlay(self):
        return self._getBool(11)

    def setCanPlay(self, value):
        self._setBool(11, value)

    def getIsFirstShow(self):
        return self._getBool(12)

    def setIsFirstShow(self, value):
        self._setBool(12, value)

    def getAnimState(self):
        return self._getString(13)

    def setAnimState(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(BattlePassEntryPointViewModel, self)._initialize()
        self._addNumberProperty('prevLevel', 0)
        self._addNumberProperty('level', 0)
        self._addNumberProperty('maxCommonLevel', 0)
        self._addRealProperty('prevProgression', 0.0)
        self._addRealProperty('progression', -1)
        self._addBoolProperty('isPostProgression', False)
        self._addBoolProperty('hasBattlePass', False)
        self._addBoolProperty('isPostProgressionCompleted', False)
        self._addStringProperty('state', '')
        self._addBoolProperty('isSmall', False)
        self._addNumberProperty('tooltipID', 0)
        self._addBoolProperty('canPlay', False)
        self._addBoolProperty('isFirstShow', False)
        self._addStringProperty('animState', '')
        self.onClick = self._addCommand('onClick')
