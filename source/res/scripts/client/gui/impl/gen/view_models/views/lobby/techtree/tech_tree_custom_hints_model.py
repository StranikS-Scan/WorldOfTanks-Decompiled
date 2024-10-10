# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/tech_tree_custom_hints_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.techtree.custom_tech_tree_hint import CustomTechTreeHint

class TechTreeCustomHintsModel(ViewModel):
    __slots__ = ('onHintShown',)

    def __init__(self, properties=1, commands=1):
        super(TechTreeCustomHintsModel, self).__init__(properties=properties, commands=commands)

    def getActiveHints(self):
        return self._getArray(0)

    def setActiveHints(self, value):
        self._setArray(0, value)

    @staticmethod
    def getActiveHintsType():
        return CustomTechTreeHint

    def _initialize(self):
        super(TechTreeCustomHintsModel, self)._initialize()
        self._addArrayProperty('activeHints', Array())
        self.onHintShown = self._addCommand('onHintShown')
