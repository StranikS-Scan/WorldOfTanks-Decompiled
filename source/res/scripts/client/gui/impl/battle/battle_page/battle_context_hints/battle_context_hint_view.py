# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/battle_context_hints/battle_context_hint_view.py
import typing
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from gui.impl.battle.battle_page.battle_context_hints.battle_context_hints_presenters import BattleContextHintsViewPresenter

class BattleContextHintsView(ViewImpl):

    def __init__(self, *args, **kwargs):
        super(BattleContextHintsView, self).__init__(*args, **kwargs)
        self.__hintClosedCallback = None
        return

    def showHint(self, presenter, hintClosedCallback):
        self.__hintClosedCallback = hintClosedCallback
        viewModel = super(BattleContextHintsView, self).getViewModel()
        with viewModel.transaction() as model:
            model.setIsVisible(True)
            if presenter is not None:
                presenter.updateModel(model)
        return

    def hideHint(self):
        viewModel = super(BattleContextHintsView, self).getViewModel()
        with viewModel.transaction() as model:
            model.setIsVisible(False)

    def _getEvents(self):
        return ((self.getViewModel().onHintClosed, self.__onHintClosed),)

    def __onHintClosed(self):
        self.hideHint()
        if self.__hintClosedCallback is not None:
            self.__hintClosedCallback()
        return
