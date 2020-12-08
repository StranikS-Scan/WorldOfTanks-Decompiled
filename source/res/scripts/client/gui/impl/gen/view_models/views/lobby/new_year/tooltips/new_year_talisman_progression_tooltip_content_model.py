# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_talisman_progression_tooltip_content_model.py
from frameworks.wulf import ViewModel

class NewYearTalismanProgressionTooltipContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NewYearTalismanProgressionTooltipContentModel, self).__init__(properties=properties, commands=commands)

    def getCurrentStage(self):
        return self._getNumber(0)

    def setCurrentStage(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(NewYearTalismanProgressionTooltipContentModel, self)._initialize()
        self._addNumberProperty('currentStage', 0)
