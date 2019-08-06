# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_info_view.py
from account_helpers.AccountSettings import FESTIVAL_INFO_VISITED, AccountSettings
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_info_view_model import FestivalInfoViewModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showFestivalInfoPage
from helpers import dependency
from items.components.festival_constants import FEST_ITEM_TYPE
from skeletons.festival import IFestivalController

class FestivalInfoView(ViewImpl):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(FestivalInfoView, self).__init__(R.views.lobby.festival.festival_info_view.FestivalInfoView(), ViewFlags.VIEW, FestivalInfoViewModel, *args, **kwargs)

    def _initialize(self):
        super(FestivalInfoView, self)._initialize()
        with self.viewModel.transaction() as model:
            for randomName in FEST_ITEM_TYPE.INFO:
                randomCost = self.__festController.getRandomCost(randomName)
                if randomName == FEST_ITEM_TYPE.ANY:
                    model.setFullRandomCost(randomCost)
                model.setRandomCost(randomCost)

            model.onVideoClicked += self.__onVideoClicked
        AccountSettings.setNotifications(FESTIVAL_INFO_VISITED, True)

    def _finalize(self):
        self.getViewModel().onVideoClicked -= self.__onVideoClicked
        super(FestivalInfoView, self)._finalize()

    @property
    def viewModel(self):
        return super(FestivalInfoView, self).getViewModel()

    @staticmethod
    def __onVideoClicked():
        showFestivalInfoPage()
