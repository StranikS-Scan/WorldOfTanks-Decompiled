# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_banner/races_banner_inactive_tooltip.py
from frameworks.wulf import ViewSettings, ViewFlags, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class RacesBannerInactiveTooltip(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.races.lobby.tooltips.RacesBannerInactiveTooltipView(), ViewFlags.VIEW, ViewModel())
        super(RacesBannerInactiveTooltip, self).__init__(settings)
