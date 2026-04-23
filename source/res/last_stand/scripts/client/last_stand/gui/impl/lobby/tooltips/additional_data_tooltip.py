# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/additional_data_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class AdditionalDataTooltipView(ViewImpl):

    def __init__(self):
        super(AdditionalDataTooltipView, self).__init__(ViewSettings(R.views.last_stand.mono.lobby.tooltips.additional_data_tooltip(), model=ViewModel()))
