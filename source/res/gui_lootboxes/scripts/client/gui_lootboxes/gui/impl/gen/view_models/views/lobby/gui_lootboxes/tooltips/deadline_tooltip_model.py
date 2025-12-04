# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/deadline_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.short_statistic_lootboxes import ShortStatisticLootboxes

class DeadlineTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(DeadlineTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLootboxes(self):
        return self._getArray(0)

    def setLootboxes(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLootboxesType():
        return ShortStatisticLootboxes

    def _initialize(self):
        super(DeadlineTooltipModel, self)._initialize()
        self._addArrayProperty('lootboxes', Array())
