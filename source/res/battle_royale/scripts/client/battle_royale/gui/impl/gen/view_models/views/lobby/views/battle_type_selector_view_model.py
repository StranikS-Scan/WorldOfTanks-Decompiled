# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/battle_type_selector_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BattleType(Enum):
    SOLO = 'solo'
    RANDOMPLATOON = 'randomPlatoon'
    PLATOON = 'platoon'


class AnimationState(Enum):
    NONE = 'none'
    FIRSTSHOW = 'firstShow'
    IDLEBLINK = 'idleBlink'


class BattleTypeSelectorViewModel(ViewModel):
    __slots__ = ('onSelectTab',)

    def __init__(self, properties=3, commands=1):
        super(BattleTypeSelectorViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedTab(self):
        return BattleType(self._getString(0))

    def setSelectedTab(self, value):
        self._setString(0, value.value)

    def getAnimationState(self):
        return AnimationState(self._getString(1))

    def setAnimationState(self, value):
        self._setString(1, value.value)

    def getIsHintShown(self):
        return self._getBool(2)

    def setIsHintShown(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BattleTypeSelectorViewModel, self)._initialize()
        self._addStringProperty('selectedTab', BattleType.SOLO.value)
        self._addStringProperty('animationState', AnimationState.NONE.value)
        self._addBoolProperty('isHintShown', False)
        self.onSelectTab = self._addCommand('onSelectTab')
