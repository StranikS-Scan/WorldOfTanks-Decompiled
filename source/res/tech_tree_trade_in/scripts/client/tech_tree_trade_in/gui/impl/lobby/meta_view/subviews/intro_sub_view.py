# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/subviews/intro_sub_view.py
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tech_tree_trade_in_view_model import MainViews
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.intro_view_model import IntroViewModel
from helpers import dependency, time_utils
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews import SubViewBase
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController

def getTimestampDelta(timestamp):
    return timestamp - time_utils.getCurrentLocalServerTimestamp()


class IntroSubView(SubViewBase):
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)

    @property
    def viewId(self):
        return MainViews.INTRO

    @property
    def viewModel(self):
        return super(IntroSubView, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(IntroSubView, self).initialize(*args, **kwargs)
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.onShowVideo, self.__onShowVideo),
         (self.viewModel.onOpenInfoPage, self.__onOpenInfoPage),
         (self.viewModel.onContinue, self.__onContinue),
         (self.__techTreeTradeInController.onSettingsChanged, self.__updateViewModel))

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setTimeOffer(self.__getEndTime())

    def __getEndTime(self):
        return getTimestampDelta(self.__techTreeTradeInController.getEndTime())

    def __onShowVideo(self):
        self.__techTreeTradeInController.showOnboardingIntroVideo()

    def __onOpenInfoPage(self):
        pass

    def __onContinue(self):
        self.parentView.switchContent({'viewType': MainViews.BRANCH_SELECTION})
