# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/mode_selector/fort_rush_mode_selector_model.py
from fort_rush.gui.impl.gen.view_models.views.lobby.mode_selector.fort_rush_mode_selector_widget_model import FortRushModeSelectorWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class FortRushModeSelectorModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(FortRushModeSelectorModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(22)

    @staticmethod
    def getWidgetType():
        return FortRushModeSelectorWidgetModel

    def _initialize(self):
        super(FortRushModeSelectorModel, self)._initialize()
        self._addViewModelProperty('widget', FortRushModeSelectorWidgetModel())
