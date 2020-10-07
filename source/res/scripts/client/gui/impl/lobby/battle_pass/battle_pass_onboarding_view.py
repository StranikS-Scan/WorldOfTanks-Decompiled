# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_onboarding_view.py
from account_helpers.offers.cache import CachePrefetchResult
from adisp import process, async
from battle_pass_common import getBattlePassOnboardingToken
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_helpers import showOfferGiftsWindowByToken
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_onboarding_view_model import BattlePassOnboardingViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider

class BattlePassOnboardingView(ViewImpl):
    __slots__ = ()
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassOnboardingView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = BattlePassOnboardingViewModel()
        super(BattlePassOnboardingView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassOnboardingView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassOnboardingView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__setOnboardingState()

    def _finalize(self):
        super(BattlePassOnboardingView, self)._finalize()
        self.__removeListeners()

    def __addListeners(self):
        model = self.viewModel
        model.onCollectClick += self.__onCollectClick
        model.onBackClick += self.__onBackClick
        self.__battlePassController.onOnboardingChange += self.__onOnboardingChange

    def __removeListeners(self):
        model = self.viewModel
        model.onCollectClick -= self.__onCollectClick
        model.onBackClick -= self.__onBackClick
        self.__battlePassController.onOnboardingChange -= self.__onOnboardingChange

    def __onCollectClick(self):
        token = getBattlePassOnboardingToken(self.__battlePassController.getSeasonID())
        showOfferGiftsWindowByToken(token)

    def __onOnboardingChange(self):
        self.__setOnboardingState()

    def __onBackClick(self):
        self.destroy()

    @process
    def __setOnboardingState(self):
        with self.viewModel.transaction() as model:
            model.setIsOffersEnabled(False)
            model.setIsAllReceived(not self.__battlePassController.isOnboardingActive())
            model.setMaxLevelForNewbie(self.__battlePassController.getMaxLevelForNewbie())
            result = yield self.__syncOfferResources()
            model.setIsOffersEnabled(self.__lobbyContext.getServerSettings().isOffersEnabled() and result == CachePrefetchResult.SUCCESS)

    @async
    @process
    def __syncOfferResources(self, callback=None):
        Waiting.show('loadContent')
        result = yield self.__offersProvider.isCdnResourcesReady()
        Waiting.hide('loadContent')
        callback(result)


class BattlePassOnboardingWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent):
        super(BattlePassOnboardingWindow, self).__init__(content=BattlePassOnboardingView(), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return
