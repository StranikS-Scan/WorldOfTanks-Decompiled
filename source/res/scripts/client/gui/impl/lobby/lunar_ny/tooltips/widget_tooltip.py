# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/tooltips/widget_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.lunar_ny.tooltips.widget_tooltip_model import WidgetTooltipModel
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import fillEnvelopesProgressionModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from lunar_ny import ILunarNYController

class WidgetTooltip(ViewImpl[WidgetTooltipModel]):
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = WidgetTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(WidgetTooltip, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(WidgetTooltip, self)._onLoading(*args, **kwargs)
        _, end = self.__lunarNYController.getEventActiveTime()
        currentUTCTime = getServerUTCTime()
        leftTime = max(0, end - currentUTCTime)
        with self.getViewModel().transaction() as model:
            model.setEventTimeLeft(leftTime)
            fillEnvelopesProgressionModel(model.envelopesProgression, self.__lunarNYController.progression.getProgressionConfig(), self.__lunarNYController.progression.getSentEnvelopesCount())
