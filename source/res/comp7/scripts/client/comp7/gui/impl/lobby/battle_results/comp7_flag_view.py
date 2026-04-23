# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/comp7_flag_view.py
from __future__ import absolute_import
from gui.impl.lobby.battle_results.flag_view import FlagView, _TEXTURE_PATH
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_flag_view_model import Comp7FlagViewModel
from gui.impl.pub import WindowImpl
from frameworks.wulf import WindowFlags
from gui.impl.gen import R

class Comp7FlagWindow(WindowImpl):

    def __init__(self):
        super(Comp7FlagWindow, self).__init__(wndFlags=WindowFlags.SURFACE, content=Comp7FlagView(), name=_TEXTURE_PATH)


class Comp7FlagView(FlagView):
    _VIEW_SETTINGS_LAYOUT_ID = R.views.comp7.mono.lobby.flag()
    _VIEW_MODEL = Comp7FlagViewModel

    def _getLsmStateClass(self):
        from comp7.gui.impl.lobby.battle_results.states import Comp7PostBattleResultsState
        return Comp7PostBattleResultsState

    @property
    def viewModel(self):
        return super(Comp7FlagView, self).getViewModel()
