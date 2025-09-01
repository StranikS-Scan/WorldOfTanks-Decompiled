# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/newbie_banner_tooltip.py
from frameworks.wulf import ViewModel
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from story_mode.uilogging.story_mode.loggers import NewbieEntryPointTooltipLogger

class NewbieBannerTooltip(ViewImpl):

    def __init__(self):
        super(NewbieBannerTooltip, self).__init__(ViewSettings(R.views.story_mode.lobby.NewbieBannerTooltip(), model=ViewModel()))
        self._uiLogger = NewbieEntryPointTooltipLogger()
        self._uiLogger.start()

    def _finalize(self):
        self._uiLogger.stop()
        super(NewbieBannerTooltip, self)._finalize()
