# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_stronghold_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_stronghold_widget_model import ModeSelectorStrongholdWidgetModel

class ModeSelectorStrongholdModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(ModeSelectorStrongholdModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(21)

    @staticmethod
    def getWidgetType():
        return ModeSelectorStrongholdWidgetModel

    def _initialize(self):
        super(ModeSelectorStrongholdModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorStrongholdWidgetModel())
