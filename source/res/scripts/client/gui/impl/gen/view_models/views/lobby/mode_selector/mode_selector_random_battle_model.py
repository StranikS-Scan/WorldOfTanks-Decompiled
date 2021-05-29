# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_random_battle_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_random_battle_widget_model import ModeSelectorRandomBattleWidgetModel

class ModeSelectorRandomBattleModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(ModeSelectorRandomBattleModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(19)

    def getIsSettingsActive(self):
        return self._getBool(20)

    def setIsSettingsActive(self, value):
        self._setBool(20, value)

    def _initialize(self):
        super(ModeSelectorRandomBattleModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorRandomBattleWidgetModel())
        self._addBoolProperty('isSettingsActive', False)
