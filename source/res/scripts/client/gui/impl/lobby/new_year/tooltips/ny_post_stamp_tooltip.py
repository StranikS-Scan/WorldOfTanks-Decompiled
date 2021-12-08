# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_post_stamp_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from uilogging.ny.constants import LogGroups
from uilogging.ny.loggers import NyGiftSystemViewTooltipLogger

class NyPostStampTooltip(ViewImpl):
    __slots__ = ()
    __uiLogger = NyGiftSystemViewTooltipLogger(LogGroups.STAMP_ICON.value)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyPostStampTooltip(), model=ViewModel())
        super(NyPostStampTooltip, self).__init__(settings)

    def _onLoaded(self, *args, **kwargs):
        super(NyPostStampTooltip, self)._onLoaded(*args, **kwargs)
        self.__uiLogger.onTooltipOpened()

    def _finalize(self):
        self.__uiLogger.onTooltipClosed()
        super(NyPostStampTooltip, self)._finalize()
