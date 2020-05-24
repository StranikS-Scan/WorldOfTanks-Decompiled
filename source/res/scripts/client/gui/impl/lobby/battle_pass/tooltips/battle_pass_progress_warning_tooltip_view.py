# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_progress_warning_tooltip_view.py
from frameworks.wulf import ViewModel, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class BattlePassProgressWarningTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassProgressWarningTooltipView())
        settings.model = ViewModel()
        super(BattlePassProgressWarningTooltipView, self).__init__(settings)
