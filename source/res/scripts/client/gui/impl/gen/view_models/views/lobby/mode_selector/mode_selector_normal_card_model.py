# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_normal_card_model.py
from enum import IntEnum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_model import ModeSelectorCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_reward_model import ModeSelectorRewardModel

class BattlePassState(IntEnum):
    NONE = 0
    STATIC = 1
    NEW = 2


class ModeSelectorNormalCardModel(ModeSelectorCardModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=0):
        super(ModeSelectorNormalCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(10)

    def getName(self):
        return self._getString(11)

    def setName(self, value):
        self._setString(11, value)

    def getEventName(self):
        return self._getString(12)

    def setEventName(self, value):
        self._setString(12, value)

    def getStatusNotActive(self):
        return self._getString(13)

    def setStatusNotActive(self, value):
        self._setString(13, value)

    def getStatusActive(self):
        return self._getString(14)

    def setStatusActive(self, value):
        self._setString(14, value)

    def getDescription(self):
        return self._getString(15)

    def setDescription(self, value):
        self._setString(15, value)

    def getConditions(self):
        return self._getString(16)

    def setConditions(self, value):
        self._setString(16, value)

    def getTimeLeft(self):
        return self._getString(17)

    def setTimeLeft(self, value):
        self._setString(17, value)

    def getRewardList(self):
        return self._getArray(18)

    def setRewardList(self, value):
        self._setArray(18, value)

    def getBattlePassState(self):
        return BattlePassState(self._getNumber(19))

    def setBattlePassState(self, value):
        self._setNumber(19, value.value)

    def _initialize(self):
        super(ModeSelectorNormalCardModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorBaseWidgetModel())
        self._addStringProperty('name', '')
        self._addStringProperty('eventName', '')
        self._addStringProperty('statusNotActive', '')
        self._addStringProperty('statusActive', '')
        self._addStringProperty('description', '')
        self._addStringProperty('conditions', '')
        self._addStringProperty('timeLeft', '')
        self._addArrayProperty('rewardList', Array())
        self._addNumberProperty('battlePassState')
