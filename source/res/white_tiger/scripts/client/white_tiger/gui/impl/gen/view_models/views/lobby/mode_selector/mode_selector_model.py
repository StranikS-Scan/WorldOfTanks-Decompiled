# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_model.py
from white_tiger.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_widget_model import ModeSelectorWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class ModeSelectorModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(ModeSelectorModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(22)

    @staticmethod
    def getWidgetType():
        return ModeSelectorWidgetModel

    def _initialize(self):
        super(ModeSelectorModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorWidgetModel())
