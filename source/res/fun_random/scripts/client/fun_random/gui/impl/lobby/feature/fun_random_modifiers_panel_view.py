# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_modifiers_panel_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import FunRandomMaps
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_modifiers_panel_model import FunRandomModifiersPanelModel
from fun_random.gui.shared.event_dispatcher import showFunRandomMapsView
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.hangar import IBattleModifiersEntry

class FunRandomModifiersPanel(ViewImpl, FunSubModesWatcher, IBattleModifiersEntry):
    __slots__ = ()
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self):
        settings = ViewSettings(R.views.fun_random.lobby.feature.FunRandomModifiersPanel())
        settings.flags = ViewFlags.VIEW
        settings.model = FunRandomModifiersPanelModel()
        super(FunRandomModifiersPanel, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        self.startSubSelectionListening(self.__onSubModeSwitched)
        self.__update()
        super(FunRandomModifiersPanel, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.stopSubSelectionListening(self.__onSubModeSwitched)
        super(FunRandomModifiersPanel, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onWidgetClick, self.__showMapsView),)

    @classmethod
    def getIsActive(cls):
        subModeId = cls.__funRandomCtrl.subModesHolder.getDesiredSubModeID()
        return cls.__funRandomCtrl.isFunRandomModifiersVisibleBySubModeID(subModeId)

    @property
    def currentSubmodeID(self):
        return self.getDesiredSubMode().getSubModeID()

    @property
    def viewModel(self):
        return super(FunRandomModifiersPanel, self).getViewModel()

    def __showMapsView(self):
        showFunRandomMapsView()
        self.__updateVisited()

    def __onSubModeSwitched(self, *_):
        self.__update()

    def __updateVisited(self):
        visitedIds = AccountSettings.getFunRandom(FunRandomMaps.FUN_RANDOM_WIDGET_VISITED_SUBMODES)
        visitedIds.add(self.currentSubmodeID)
        AccountSettings.setFunRandom(FunRandomMaps.FUN_RANDOM_WIDGET_VISITED_SUBMODES, visitedIds)

    def __isSubModeVisited(self):
        visitedIds = AccountSettings.getFunRandom(FunRandomMaps.FUN_RANDOM_WIDGET_VISITED_SUBMODES)
        return self.currentSubmodeID in visitedIds

    def __update(self):
        self.viewModel.setIsPanelClicked(self.__isSubModeVisited())
