# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_battle_royale_model.py
from battle_royale.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_battle_royale_widget_model import ModeSelectorBattleRoyaleWidgetModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class ModeSelectorBattleRoyaleModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=24, commands=0):
        super(ModeSelectorBattleRoyaleModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(22)

    @staticmethod
    def getWidgetType():
        return ModeSelectorBattleRoyaleWidgetModel

    @property
    def eventInfo(self):
        return self._getViewModel(23)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    def _initialize(self):
        super(ModeSelectorBattleRoyaleModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorBattleRoyaleWidgetModel())
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
