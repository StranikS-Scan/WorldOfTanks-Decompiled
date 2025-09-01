# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/event_banner_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers.time_utils import getTimestampFromUTC, getServerUTCTime
from story_mode.uilogging.story_mode.loggers import EventEntryPointTooltipLogger
from story_mode_common.configs.story_mode_settings import settingsSchema
from story_mode.gui.impl.gen.view_models.views.lobby.event_banner_tooltip_model import EventBannerTooltipModel

class EventBannerTooltip(ViewImpl):

    def __init__(self):
        super(EventBannerTooltip, self).__init__(ViewSettings(R.views.story_mode.lobby.EventBannerTooltip(), model=EventBannerTooltipModel()))
        self._uiLogger = EventEntryPointTooltipLogger()
        self._uiLogger.start()

    @property
    def viewModel(self):
        return super(EventBannerTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventBannerTooltip, self)._onLoading(*args, **kwargs)
        settings = settingsSchema.getModel()
        if settings is not None:
            self.viewModel.setTimerValue(getTimestampFromUTC(settings.entryPoint.eventEndAt.timetuple()) - getServerUTCTime())
        return

    def _finalize(self):
        self._uiLogger.stop()
        super(EventBannerTooltip, self)._finalize()
