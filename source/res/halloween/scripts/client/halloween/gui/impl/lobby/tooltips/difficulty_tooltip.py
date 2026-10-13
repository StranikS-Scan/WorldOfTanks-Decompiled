# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/difficulty_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.gui.impl.gen.view_models.views.lobby.widgets.difficulty_item_model import DifficultyItemModel

class DifficultyTooltipView(ViewImpl):
    __slots__ = ('__level', '__state', '__isLocked')

    def __init__(self, level, state, isLocked, layoutID=R.views.halloween.mono.lobby.tooltips.difficulty_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = DifficultyItemModel()
        super(DifficultyTooltipView, self).__init__(settings)
        self.__level = level
        self.__state = state
        self.__isLocked = isLocked

    @property
    def viewModel(self):
        return super(DifficultyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DifficultyTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setLevel(self.__level)
            model.setState(self.__state)
            model.setIsLocked(self.__isLocked)
