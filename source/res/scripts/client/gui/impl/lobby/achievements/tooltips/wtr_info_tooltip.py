# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/tooltips/wtr_info_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class WTRInfoTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.achievements.tooltips.WTRInfoTooltip(), model=ViewModel())
        super(WTRInfoTooltip, self).__init__(settings)
