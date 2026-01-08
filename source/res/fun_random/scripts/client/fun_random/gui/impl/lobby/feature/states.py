# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/states.py
from __future__ import absolute_import
import typing
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from fun_random_common.fun_constants import FunSubModeImpl
from fun_random.gui.battle_results.fun_battle_results_sub_presenter import FunBattleResultsSubPresenter
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher, FunAssetPacksMixin
from fun_random.gui.impl.lobby.feature.fun_random_tier_list_view import FunRandomTierListView
from gui.battle_results.service import PostBattleResultsStateMixin
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SubScopeSubLayerState, SubScopeTopLayerState, LobbyStateDescription, ViewLobbyState, LobbyStateFlags
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.shared.utils.functions import getViewName

def registerStates(machine):
    machine.addState(FunRandomProgressionState())
    machine.addState(FunRandomTierListState())
    machine.addState(FunPostBattleResultsState())


def registerTransitions(machine):
    pass


@SubScopeSubLayerState.parentOf
class FunRandomProgressionState(ViewLobbyState):
    STATE_ID = FUNRANDOM_ALIASES.FUN_PROGRESSION
    VIEW_KEY = ViewKey(FUNRANDOM_ALIASES.FUN_PROGRESSION)

    def registerTransitions(self):
        machine = self.getMachine()
        funRandomProgression = machine.getStateByCls(FunRandomProgressionState)
        machine.addNavigationTransitionFromParent(funRandomProgression)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(FunAssetPacksMixin.getModeLocalsResRoot().progression.title()), infos=(LobbyStateDescription.Info(tooltipHeader=backport.text(R.strings.menu.viewHeader.aboutBtn.label()), type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=FunSubModesWatcher.showCommonInfoPage),))


@SubScopeTopLayerState.parentOf
class FunRandomTierListState(GuiImplViewLobbyState):
    STATE_ID = 'funRandomTierList'
    VIEW_KEY = ViewKey(R.views.fun_random.mono.lobby.tier_list())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FunRandomTierListState, self).__init__(FunRandomTierListView, flags=flags, scope=ScopeTemplates.LOBBY_SUB_SCOPE)

    def registerTransitions(self):
        machine = self.getMachine()
        funRandomTierList = machine.getStateByCls(FunRandomTierListState)
        machine.addNavigationTransitionFromParent(funRandomTierList)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(FunAssetPacksMixin.getModeLocalsResRoot().tierList.title()))

    def _getViewLoadCtx(self, event):
        return {}

    def _getViewLoadParams(self, event):
        return GuiImplViewLoadParams(self.VIEW_KEY.alias, self._viewImplClass, self._scope, event.params.get('parent'))


@SubScopeSubLayerState.parentOf
class FunPostBattleResultsState(ViewLobbyState, PostBattleResultsStateMixin):
    STATE_ID = FUNRANDOM_ALIASES.FUN_POST_BATTLE_RESULTS
    VIEW_KEY = ViewKey(FUNRANDOM_ALIASES.FUN_POST_BATTLE_RESULTS)
    __layoutIDsAndSubPresenters = {FunSubModeImpl.DEFAULT: (FunBattleResultsSubPresenter, R.views.fun_random.mono.lobby.battle_results())}

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FunPostBattleResultsState, self).__init__(flags=flags | LobbyStateFlags.POST_BATTLE_RESULTS)
        self.__cachedParams = {}

    def getViewKey(self, params=None):
        arenaUniqueID = self.__cachedParams.get('arenaUniqueID', '')
        alias = super(FunPostBattleResultsState, self).getViewKey().alias
        return ViewKey(alias, getViewName(alias, arenaUniqueID))

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fun_battle_results.title()))

    def registerTransitions(self):
        machine = self.getMachine()
        machine.addNavigationTransitionFromParent(self)
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)

    def _getViewLoadCtx(self, event):
        ctx = dict(event.params)
        subPresenterCls, layoutId = self.__layoutIDsAndSubPresenters.get(ctx['subModeImpl'], self.__layoutIDsAndSubPresenters[FunSubModeImpl.DEFAULT])
        ctx['subPresenterCls'] = subPresenterCls
        ctx['layoutID'] = layoutId
        return ctx

    def _onEntered(self, event):
        self.__cachedParams = dict(event.params)
        super(FunPostBattleResultsState, self)._onEntered(event)

    def _onExited(self):
        super(FunPostBattleResultsState, self)._onExited()
        self.__cachedParams = {}
