# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_battle_royale_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_battle_royale_widget_model import ModeSelectorBattleRoyaleWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class ModeSelectorBattleRoyaleModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(ModeSelectorBattleRoyaleModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(20)

    @staticmethod
    def getWidgetType():
        return ModeSelectorBattleRoyaleWidgetModel

    def _initialize(self):
        super(ModeSelectorBattleRoyaleModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorBattleRoyaleWidgetModel())
