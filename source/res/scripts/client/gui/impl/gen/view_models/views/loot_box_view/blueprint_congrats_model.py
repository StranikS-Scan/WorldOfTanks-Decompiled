# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/blueprint_congrats_model.py
from gui.impl.gen.view_models.views.loot_box_view.congrats_view_model import CongratsViewModel

class BlueprintCongratsModel(CongratsViewModel):
    __slots__ = ()

    def getFragments(self):
        return self._getNumber(10)

    def setFragments(self, value):
        self._setNumber(10, value)

    def getFragmentsTotal(self):
        return self._getNumber(11)

    def setFragmentsTotal(self, value):
        self._setNumber(11, value)

    def getCanConvert(self):
        return self._getBool(12)

    def setCanConvert(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(BlueprintCongratsModel, self)._initialize()
        self._addNumberProperty('fragments', 0)
        self._addNumberProperty('fragmentsTotal', 1)
        self._addBoolProperty('canConvert', False)
