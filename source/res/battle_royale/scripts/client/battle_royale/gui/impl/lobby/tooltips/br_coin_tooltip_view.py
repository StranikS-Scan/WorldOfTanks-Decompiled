# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/br_coin_tooltip_view.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class BrCoinTooltipView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.BrCoinTooltipView())
        settings.model = ViewModel()
        super(BrCoinTooltipView, self).__init__(settings)
