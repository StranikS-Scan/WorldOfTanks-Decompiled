# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_comp7_light_model.py
from comp7_light.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_light_widget_model import ModeSelectorComp7LightWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class ModeSelectorComp7LightModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(ModeSelectorComp7LightModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(22)

    @staticmethod
    def getWidgetType():
        return ModeSelectorComp7LightWidgetModel

    def _initialize(self):
        super(ModeSelectorComp7LightModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorComp7LightWidgetModel())
