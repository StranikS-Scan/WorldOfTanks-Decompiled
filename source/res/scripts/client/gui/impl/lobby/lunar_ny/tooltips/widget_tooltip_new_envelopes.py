# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/tooltips/widget_tooltip_new_envelopes.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.lunar_ny.tooltips.widget_tooltip_new_envelopes_model import WidgetTooltipNewEnvelopesModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from lunar_ny import ILunarNYController

class WidgetTooltipNewEnvelopes(ViewImpl):
    __slots__ = ()
    __lunarNYController = dependency.descriptor(ILunarNYController)

    def __init__(self, contentID):
        settings = ViewSettings(contentID)
        settings.model = WidgetTooltipNewEnvelopesModel()
        super(WidgetTooltipNewEnvelopes, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WidgetTooltipNewEnvelopes, self)._onLoading()
        self.viewModel.setSecretSantaSentLimitTime(self.__lunarNYController.giftSystem.getSecretSantaSentPeriodLimit())
