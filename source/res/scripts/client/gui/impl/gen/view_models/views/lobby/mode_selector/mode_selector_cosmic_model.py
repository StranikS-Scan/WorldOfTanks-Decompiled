# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_cosmic_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_cosmic_widget_model import ModeSelectorCosmicWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class ModeSelectorCosmicModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(ModeSelectorCosmicModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(20)

    @staticmethod
    def getWidgetType():
        return ModeSelectorCosmicWidgetModel

    def getIsSuspended(self):
        return self._getBool(21)

    def setIsSuspended(self, value):
        self._setBool(21, value)

    def _initialize(self):
        super(ModeSelectorCosmicModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorCosmicWidgetModel())
        self._addBoolProperty('isSuspended', False)
