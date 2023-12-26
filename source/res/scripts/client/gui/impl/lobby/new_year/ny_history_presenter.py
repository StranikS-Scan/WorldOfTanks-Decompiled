# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_history_presenter.py
from gui.impl.lobby.new_year.history_presenter import HistoryPresenter
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.navigation import NewYearNavigation, NewYearTabCache, ViewAliases
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.shared.ny_vignette_settings_switcher import checkVignetteSettings
from helpers import dependency
from skeletons.new_year import INewYearController, IFriendServiceController
from gui.impl.new_year.history_manager.commands.new_year.ny_return_to_view import NyReturnToView

class NyHistoryPresenter(HistoryPresenter):
    __slots__ = ('_isScopeWatcher', '__soundsManager')
    _tabCache = NewYearTabCache()
    _nyController = dependency.descriptor(INewYearController)
    _friendsService = dependency.descriptor(IFriendServiceController)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NyHistoryPresenter, self).__init__(viewModel, parentView)
        self._isScopeWatcher = True
        self.__soundsManager = NewYearSoundsManager({} if soundConfig is None else soundConfig)
        return

    def initialize(self, *args, **kwargs):
        self.__soundsManager.onEnterView()
        super(NyHistoryPresenter, self).initialize(*args, **kwargs)
        if self._isScopeWatcher:
            checkVignetteSettings('ny_navigation')
        self._updateBackButton()

    def finalize(self):
        super(NyHistoryPresenter, self).finalize()
        self.__soundsManager.onExitView()

    def clear(self):
        super(NyHistoryPresenter, self).clear()
        self.__soundsManager.clear()

    def addToHistoryForced(self):
        self.__preserveHistory()

    @classmethod
    def clearTabCache(cls):
        cls._tabCache.clear()

    @property
    def currentTab(self):
        return None

    def _goToRewardsView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.REWARDS_VIEW, tabName, *args, **kwargs)

    def _goToByViewAlias(self, viewAlias, tabName=None, *args, **kwargs):
        self._switchToView(viewAlias, tabName, *args, **kwargs)

    def _goToMainView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.GLADE_VIEW, tabName, *args, **kwargs)

    def _goToFriendMainView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.FRIEND_GLADE_VIEW, tabName, *args, **kwargs)

    def _goToFriendsView(self, leaveService, *args, **kwargs):
        if leaveService:
            self._friendsService.preLeaveFriendHangar()
        self._switchToView(ViewAliases.FRIENDS_VIEW, *args, **kwargs)

    def _goToCelebrityView(self, tabName=None, *args, **kwargs):
        self._switchToView(ViewAliases.CELEBRITY_VIEW, tabName, *args, **kwargs)

    def _goToGiftMachineView(self, *args, **kwargs):
        self._switchToView(ViewAliases.GIFT_MACHINE, *args, **kwargs)

    def _switchToView(self, aliasName, *args, **kwargs):
        saveHistory = kwargs.pop('saveHistory', False)
        popHistory = kwargs.pop('popHistory', False)
        if popHistory:
            self._historyManager.pop()
        if saveHistory:
            self.__preserveHistory()
        NewYearNavigation.switchToView(aliasName, *args, **kwargs)

    def _updateBackButton(self):
        if self._historyManager.hasPrevViews():
            ctx = {'isVisible': True,
             'goTo': backport.text(self._getBackPageName()),
             'callback': self._goBack}
        else:
            ctx = {'isVisible': False}
        NewYearNavigation.updateBackButton(ctx)

    def _createBackButtonText(self):
        return R.strings.ny.backButton.dyn(self.getNavigationAlias())()

    def __preserveHistory(self):
        context = self._getInfoForHistory()
        if context is not None:
            context.update({'aliasName': self.getNavigationAlias()})
            self._historyManager.addToHistory(NyReturnToView(context=context, backButtonText=self._createBackButtonText()))
        return
