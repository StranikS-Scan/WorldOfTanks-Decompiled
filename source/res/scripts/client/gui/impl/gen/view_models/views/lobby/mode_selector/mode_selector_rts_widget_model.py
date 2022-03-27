# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_rts_widget_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class ModeSelectorRtsWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ModeSelectorRtsWidgetModel, self).__init__(properties=properties, commands=commands)

    def getCurrent(self):
        return self._getNumber(1)

    def setCurrent(self, value):
        self._setNumber(1, value)

    def getTotal(self):
        return self._getNumber(2)

    def setTotal(self, value):
        self._setNumber(2, value)

    def getIsProgressVisible(self):
        return self._getBool(3)

    def setIsProgressVisible(self, value):
        self._setBool(3, value)

    def getIsCycleActive(self):
        return self._getBool(4)

    def setIsCycleActive(self, value):
        self._setBool(4, value)

    def getTimeLeftToActive(self):
        return self._getNumber(5)

    def setTimeLeftToActive(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ModeSelectorRtsWidgetModel, self)._initialize()
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
        self._addBoolProperty('isProgressVisible', False)
        self._addBoolProperty('isCycleActive', False)
        self._addNumberProperty('timeLeftToActive', 0)
