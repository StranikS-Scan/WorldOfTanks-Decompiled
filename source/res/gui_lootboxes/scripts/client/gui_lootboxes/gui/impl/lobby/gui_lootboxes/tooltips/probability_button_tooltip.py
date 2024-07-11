# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/probability_button_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class ProbabilityButtonTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.ProbabilityButtonTooltip())
        settings.model = ViewModel()
        super(ProbabilityButtonTooltip, self).__init__(settings)
