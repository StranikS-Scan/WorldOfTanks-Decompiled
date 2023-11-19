# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_comp7_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_widget_model import ModeSelectorComp7WidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class ModeSelectorComp7Model(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(ModeSelectorComp7Model, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(20)

    @staticmethod
    def getWidgetType():
        return ModeSelectorComp7WidgetModel

    def _initialize(self):
        super(ModeSelectorComp7Model, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorComp7WidgetModel())
