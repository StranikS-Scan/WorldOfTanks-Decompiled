# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_event_widget_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class ModeSelectorEventWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ModeSelectorEventWidgetModel, self).__init__(properties=properties, commands=commands)

    def getKeysCount(self):
        return self._getNumber(1)

    def setKeysCount(self, value):
        self._setNumber(1, value)

    def getCurrentProgress(self):
        return self._getNumber(2)

    def setCurrentProgress(self, value):
        self._setNumber(2, value)

    def getMaximumProgress(self):
        return self._getNumber(3)

    def setMaximumProgress(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ModeSelectorEventWidgetModel, self)._initialize()
        self._addNumberProperty('keysCount', 0)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maximumProgress', 0)
