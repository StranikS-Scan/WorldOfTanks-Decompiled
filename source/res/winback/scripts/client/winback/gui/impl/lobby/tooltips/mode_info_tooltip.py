# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/tooltips/mode_info_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class ModeInfoTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.winback.lobby.tooltips.ModeInfoTooltip())
        settings.model = ViewModel()
        super(ModeInfoTooltip, self).__init__(settings)
