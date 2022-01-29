# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_progression_award_view.py
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.progression_award_view_model import ProgressionAwardViewModel
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import createRewardTooltip
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from lunar_ny.lunar_ny_bonuses_packers import composeProgressionBonuses, getLunarNYProgressionAwardPackerMap

class LunarNYProgressionAwardView(ViewImpl):
    __slots__ = ('__toolTipsData',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(kwargs.get('layoutID', R.invalid()))
        settings.flags = ViewFlags.VIEW
        settings.model = ProgressionAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(LunarNYProgressionAwardView, self).__init__(settings)
        self.__toolTipsData = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__toolTipsData.get(event.getArgument('tooltipID'), None)
        return createRewardTooltip(contentID, tooltipData)

    def _onLoading(self, *args, **kwargs):
        super(LunarNYProgressionAwardView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setReceivedLevel(kwargs.get('receivedLevel', 1))
            bonuses = composeProgressionBonuses(kwargs.get('rawData', {}), kwargs.get('receivedLevel', 1))
            packBonusModelAndTooltipData(bonuses, model.getRewards(), self.__toolTipsData, getLunarNYProgressionAwardPackerMap())

    def _finalize(self):
        super(LunarNYProgressionAwardView, self)._finalize()
        self.__toolTipsData.clear()


class LunarNYProgressionAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rawData, receivedLevel, parent=None):
        super(LunarNYProgressionAwardWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LunarNYProgressionAwardView(layoutID=R.views.lobby.lunar_ny.ProgressionAwardView(), rawData=rawData, receivedLevel=receivedLevel), layer=WindowLayer.OVERLAY, parent=parent)
