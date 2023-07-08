# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/mode_selector/fun_random_sub_selector_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_condition import FunRandomProgressionCondition
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_stage import FunRandomProgressionStage
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionState
from fun_random.gui.impl.gen.view_models.views.lobby.feature.mode_selector.fun_random_sub_selector_card_model import FunRandomSubSelectorCardModel

class FunRandomSubSelectorModel(ViewModel):
    __slots__ = ('onItemClicked', 'onInfoClicked', 'onBackBtnClicked', 'onClosed')

    def __init__(self, properties=5, commands=4):
        super(FunRandomSubSelectorModel, self).__init__(properties=properties, commands=commands)

    @property
    def state(self):
        return self._getViewModel(0)

    @staticmethod
    def getStateType():
        return FunRandomProgressionState

    @property
    def condition(self):
        return self._getViewModel(1)

    @staticmethod
    def getConditionType():
        return FunRandomProgressionCondition

    @property
    def currentStage(self):
        return self._getViewModel(2)

    @staticmethod
    def getCurrentStageType():
        return FunRandomProgressionStage

    def getCardList(self):
        return self._getArray(3)

    def setCardList(self, value):
        self._setArray(3, value)

    @staticmethod
    def getCardListType():
        return FunRandomSubSelectorCardModel

    def getAssetsPointer(self):
        return self._getString(4)

    def setAssetsPointer(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(FunRandomSubSelectorModel, self)._initialize()
        self._addViewModelProperty('state', FunRandomProgressionState())
        self._addViewModelProperty('condition', FunRandomProgressionCondition())
        self._addViewModelProperty('currentStage', FunRandomProgressionStage())
        self._addArrayProperty('cardList', Array())
        self._addStringProperty('assetsPointer', 'undefined')
        self.onItemClicked = self._addCommand('onItemClicked')
        self.onInfoClicked = self._addCommand('onInfoClicked')
        self.onBackBtnClicked = self._addCommand('onBackBtnClicked')
        self.onClosed = self._addCommand('onClosed')
