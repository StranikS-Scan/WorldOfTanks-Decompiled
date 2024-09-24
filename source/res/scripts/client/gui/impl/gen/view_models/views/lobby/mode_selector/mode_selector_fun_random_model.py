# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_fun_random_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_fun_random_widget_model import ModeSelectorFunRandomWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class ModeSelectorFunRandomModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(ModeSelectorFunRandomModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(21)

    @staticmethod
    def getWidgetType():
        return ModeSelectorFunRandomWidgetModel

    def _initialize(self):
        super(ModeSelectorFunRandomModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorFunRandomWidgetModel())
