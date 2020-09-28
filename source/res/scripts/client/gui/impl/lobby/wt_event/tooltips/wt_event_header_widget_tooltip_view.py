# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_header_widget_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_header_widget_tooltip_view_model import WtEventHeaderWidgetTooltipViewModel
from gui.wt_event.wt_event_helpers import getDaysLeftFormatted
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class WtEventHeaderWidgetTooltipView(ViewImpl):
    __slots__ = ()
    __gameEventCtrl = dependency.descriptor(IGameEventController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventHeaderWidgetTooltipView())
        settings.model = WtEventHeaderWidgetTooltipViewModel()
        super(WtEventHeaderWidgetTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventHeaderWidgetTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventHeaderWidgetTooltipView, self)._onLoading(*args, **kwargs)
        hunterCurrentProgress = self.__gameEventCtrl.getHunterCollectedCount()
        hunterTotalProgress = self.__gameEventCtrl.getHunterCollectionSize()
        bossCurrentProgress = self.__gameEventCtrl.getBossCollectedCount()
        bossTotalProgress = self.__gameEventCtrl.getBossCollectionSize()
        with self.getViewModel().transaction() as model:
            model.setCommonCurrent(hunterCurrentProgress + bossCurrentProgress)
            model.setCommonTotal(hunterTotalProgress + bossTotalProgress)
            model.setHunterCurrent(hunterCurrentProgress)
            model.setHunterTotal(hunterTotalProgress)
            model.setBossCurrent(bossCurrentProgress)
            model.setBossTotal(bossTotalProgress)
            model.setNextReward(self.__gameEventCtrl.getNextRewardItemsLeft())
            model.setDaysLeft(getDaysLeftFormatted(gameEventController=self.__gameEventCtrl))
