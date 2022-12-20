# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_epic_widget_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class ModeSelectorEpicWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ModeSelectorEpicWidgetModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getRestRewards(self):
        return self._getNumber(2)

    def setRestRewards(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ModeSelectorEpicWidgetModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('restRewards', 0)
