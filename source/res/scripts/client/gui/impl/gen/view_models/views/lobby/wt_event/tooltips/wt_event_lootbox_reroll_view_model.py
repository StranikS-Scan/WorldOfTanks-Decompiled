# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/wt_event_lootbox_reroll_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_box_tooltip_view_model import WtEventBoxTooltipViewModel

class WtEventLootboxRerollViewModel(WtEventBoxTooltipViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(WtEventLootboxRerollViewModel, self).__init__(properties=properties, commands=commands)

    def getMaxReRolls(self):
        return self._getNumber(5)

    def setMaxReRolls(self, value):
        self._setNumber(5, value)

    def getReRolls(self):
        return self._getArray(6)

    def setReRolls(self, value):
        self._setArray(6, value)

    def _initialize(self):
        super(WtEventLootboxRerollViewModel, self)._initialize()
        self._addNumberProperty('maxReRolls', 0)
        self._addArrayProperty('reRolls', Array())
