# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_parts_tooltip_content_model.py
from frameworks.wulf import ViewModel

class NewYearPartsTooltipContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NewYearPartsTooltipContentModel, self).__init__(properties=properties, commands=commands)

    def getShardsCount(self):
        return self._getNumber(0)

    def setShardsCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(NewYearPartsTooltipContentModel, self)._initialize()
        self._addNumberProperty('shardsCount', 0)
