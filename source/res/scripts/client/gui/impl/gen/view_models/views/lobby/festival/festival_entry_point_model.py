# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_entry_point_model.py
from gui.impl.gen.view_models.views.lobby.festival.festival_player_card_view_model import FestivalPlayerCardViewModel
from gui.impl.gen.view_models.ui_kit.counter_model import CounterModel

class FestivalEntryPointModel(FestivalPlayerCardViewModel):
    __slots__ = ('onWidgetClick',)

    @property
    def Counter(self):
        return self._getViewModel(7)

    def getIsHighlight(self):
        return self._getBool(8)

    def setIsHighlight(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(FestivalEntryPointModel, self)._initialize()
        self._addViewModelProperty('Counter', CounterModel())
        self._addBoolProperty('isHighlight', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
