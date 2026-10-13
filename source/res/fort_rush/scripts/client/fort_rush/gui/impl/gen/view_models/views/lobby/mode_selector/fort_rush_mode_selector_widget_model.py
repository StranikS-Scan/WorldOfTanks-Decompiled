# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/mode_selector/fort_rush_mode_selector_widget_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class FortRushModeSelectorWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FortRushModeSelectorWidgetModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getTotalCount(self):
        return self._getNumber(2)

    def setTotalCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(FortRushModeSelectorWidgetModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalCount', 0)
