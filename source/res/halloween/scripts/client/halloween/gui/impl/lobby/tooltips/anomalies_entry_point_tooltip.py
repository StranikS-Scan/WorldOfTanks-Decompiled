# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/anomalies_entry_point_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class AnomaliesEntryPointTooltipView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.halloween.mono.lobby.tooltips.anomalies_entry_point_tooltip())
        settings.model = ViewModel()
        super(AnomaliesEntryPointTooltipView, self).__init__(settings)
