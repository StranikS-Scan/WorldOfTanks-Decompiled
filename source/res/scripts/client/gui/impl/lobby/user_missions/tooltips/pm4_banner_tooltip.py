# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/pm4_banner_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class PM4BannerTooltipView(ViewImpl):

    def __init__(self, layoutID=R.views.mono.user_missions.tooltips.pm4_banner_tooltip()):
        settings = ViewSettings(layoutID, model=ViewModel())
        super(PM4BannerTooltipView, self).__init__(settings)
