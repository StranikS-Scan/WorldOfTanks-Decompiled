# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/widget/conversion_banner_widget.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.conversion_banner_widget_model import ConversionBannerWidgetModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showJunkTankmenConversion
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.auxiliary.junk_tankman_helper import JunkTankmanHelper

class ConversionBannerWidget(ViewImpl):
    LAYOUT_ID = R.views.lobby.crew.widgets.ConversionBannerWidget
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(self.LAYOUT_ID(), flags=ViewFlags.VIEW, model=ConversionBannerWidgetModel())
        super(ConversionBannerWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ConversionBannerWidget, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onStartConversion, self.__onStartConversion),)

    def setWidgetStates(self):
        with self.viewModel.transaction() as model:
            model.setSecondsLeft(JunkTankmanHelper().getTokenExpiration())
            model.setIsDisabled(not JunkTankmanHelper().hasJunkTankmans)

    def _onLoading(self, *args, **kwargs):
        super(ConversionBannerWidget, self)._onLoading(*args, **kwargs)
        self.setWidgetStates()

    def __onStartConversion(self):
        showJunkTankmenConversion()
