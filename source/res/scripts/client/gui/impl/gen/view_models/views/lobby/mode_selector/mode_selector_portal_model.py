# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_portal_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_portal_widget_model import ModeSelectorPortalWidgetModel

class ModeSelectorPortalModel(ModeSelectorNormalCardModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(ModeSelectorPortalModel, self).__init__(properties=properties, commands=commands)

    @property
    def widget(self):
        return self._getViewModel(20)

    @staticmethod
    def getWidgetType():
        return ModeSelectorPortalWidgetModel

    def _initialize(self):
        super(ModeSelectorPortalModel, self)._initialize()
        self._addViewModelProperty('widget', ModeSelectorPortalWidgetModel())
