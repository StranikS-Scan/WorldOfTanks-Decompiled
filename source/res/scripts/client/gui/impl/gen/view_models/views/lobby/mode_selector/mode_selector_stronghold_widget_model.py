# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_stronghold_widget_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class ModeSelectorStrongholdWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ModeSelectorStrongholdWidgetModel, self).__init__(properties=properties, commands=commands)

    def getCurrentStage(self):
        return self._getNumber(1)

    def setCurrentStage(self, value):
        self._setNumber(1, value)

    def getIsInClan(self):
        return self._getBool(2)

    def setIsInClan(self, value):
        self._setBool(2, value)

    def getIsActive(self):
        return self._getBool(3)

    def setIsActive(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ModeSelectorStrongholdWidgetModel, self)._initialize()
        self._addNumberProperty('currentStage', -1)
        self._addBoolProperty('isInClan', False)
        self._addBoolProperty('isActive', False)
