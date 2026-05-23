# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/states.py
from __future__ import absolute_import
from future.utils import viewvalues
from typing import TYPE_CHECKING
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.battle_pass.battle_pass_helpers import getExtraVideoURL, getIntroVideoURL, getInfoPageURL, isIntroEnabled, isIntroVideoEnabled, isExtraIntroVideoEnabled
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.common import isExtraChapterSeen, isExtraVideoShown, isIntroShown, isIntroVideoShown, setExtraChapterSeen, setExtraVideoShown, setIntroVideoShown, showOverlayVideo, showIntroView
from gui.lobby_state_machine.states import LobbyState, LobbyStateDescription, SubScopeSubLayerState, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.utils import isRomanNumberForbidden
from helpers import dependency, int2roman
from shared_utils import nextTick
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.impl import IGuiLoader
if TYPE_CHECKING:
    from typing import Union
    from frameworks.state_machine import State
_BP = R.aliases.battle_pass

def registerStates(machine):
    machine.addState(BattlePassState())


def registerTransitions(machine):
    battlePassState = machine.getStateByCls(BattlePassState)
    machine.addNavigationTransitionFromParent(battlePassState)


@SubScopeSubLayerState.parentOf
class BattlePassState(ViewLobbyState):
    STATE_ID = 'battlePass'
    VIEW_KEY = ViewKey(VIEW_ALIAS.BATTLE_PASS)

    def registerStates(self):
        lsm = self.getMachine()
        childStates = STATES.copy()
        lsm.addState(childStates.pop(_INITIAL_STATE_ID)(flags=StateFlags.INITIAL))
        for state in viewvalues(childStates):
            lsm.addState(state())

    def registerTransitions(self):
        lsm = self.getMachine()
        for state in self.getChildrenStates():
            lsm.addNavigationTransitionFromParent(state)

        chapterChoice = lsm.getStateByCls(ChapterChoiceBattlePassState)
        self.addTransition(HijackTransition(ProgressionBattlePassState, _shouldNavigateToProgression), chapterChoice)
        progressionState = lsm.getStateByCls(ProgressionBattlePassState)
        self.addTransition(HijackTransition(ChapterChoiceBattlePassState, _isHoliday), progressionState)
        holidayFinal = lsm.getStateByCls(HolidayFinalBattlePassState)
        self.addTransition(HijackTransition(ChapterChoiceBattlePassState, _isHolidayComplete), holidayFinal)

    def _onEntered(self, event):
        super(BattlePassState, self)._onEntered(event)
        childStateID = event.params.get('childStateID', R.invalid())
        if childStateID in STATES:
            STATES[childStateID].goTo(**event.params)


class _BattlePassPresenterState(LobbyState):

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_BattlePassPresenterState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def serializeParams(self):
        return self.__cachedParams

    def addNavigationTransition(self, targetViewState, transitionType=TransitionType.INTERNAL, record=True):
        super(_BattlePassPresenterState, self).addNavigationTransition(targetViewState, transitionType, record)

    def getNavigationDescription(self):
        shortStateID = self.STATE_ID.rsplit('/', 1)[-1]
        return LobbyStateDescription(title=backport.text(R.strings.battle_pass.navigation.dyn(shortStateID)(), **self._getNavigationDescriptionArgs()), infos=self._getNavigationInfos())

    def _getNavigationDescriptionArgs(self):
        return {}

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(_BattlePassPresenterState, self)._onEntered(event)

    def _onExited(self):
        super(_BattlePassPresenterState, self)._onExited()
        self.__cachedParams = {}

    def _getNavigationInfos(self):
        pass


@BattlePassState.parentOf
class ChapterChoiceBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'chapterChoice'
    VIEW_KEY = ViewKey(_BP.ChapterChoice())
    __battlePass = dependency.descriptor(IBattlePassController)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(ChapterChoiceBattlePassState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def serializeParams(self):
        view = self.getMachine().getRelatedView(self.getParent())
        if view and getattr(view, 'selectedChapter'):
            self.__cachedParams['selectedChapter'] = view.selectedChapter
        return self.__cachedParams

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        from gui.impl.lobby.vehicle_hub import OverviewState
        from gui.impl.lobby.vehicle_hub.states import VehicleHubState
        lsm = self.getMachine()
        progressionState = lsm.getStateByCls(ProgressionBattlePassState)
        postProgressionState = lsm.getStateByCls(PostProgressionBattlePassState)
        self.addNavigationTransition(lsm.getStateByCls(TankmenBattlePassState))
        self.addNavigationTransition(progressionState)
        self.addNavigationTransition(postProgressionState)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState))
        lsm.getStateByCls(VehicleHubState).addNavigationTransition(self)

    @classmethod
    def goTo(cls, **params):
        visibleRoute = getLobbyStateMachine().visibleRouteInfo
        if visibleRoute is not None and visibleRoute.state is not None and visibleRoute.visualBackNavigationTarget.getStateID() == cls.STATE_ID:
            visibleRoute.state.goBack()
        super(ChapterChoiceBattlePassState, cls).goTo(**params)
        return

    def _getNavigationDescriptionArgs(self):
        seasonNum = self.__battlePass.getSeasonNum()
        return {'seasonNum': seasonNum if isRomanNumberForbidden() else int2roman(seasonNum)}

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(ChapterChoiceBattlePassState, self)._onEntered(event)
        self.__showIntros()
        self.__updateSelectedChapter()

    def _onExited(self):
        super(ChapterChoiceBattlePassState, self)._onExited()
        self.__cachedParams = {}

    def _getNavigationInfos(self):
        return (LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=lambda : showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BATTLE_PASS_BROWSER), tooltipBody=backport.text(R.strings.battle_pass.chapterChoice.about())),)

    @nextTick
    def __showIntros(self):
        isIntroNeeded = isIntroEnabled() and not isIntroShown()
        if isIntroVideoEnabled() and not isIntroVideoShown():
            showOverlayVideo(getIntroVideoURL(), callbackOnLoad=self.__onVideoShown, callbackOnClose=None if isIntroNeeded else self.__onIntroShown)
        elif isIntroNeeded:
            showIntroView(callback=self.__onIntroShown).load()
        elif isExtraIntroVideoEnabled() and not isExtraVideoShown():
            showOverlayVideo(getExtraVideoURL(), callbackOnClose=self.__onExtraVideoShown)
        return

    @nextTick
    def __onVideoShown(self):
        setIntroVideoShown()
        if isIntroEnabled() and not isIntroShown():
            showIntroView(callback=self.__onIntroShown).load()

    @nextTick
    def __onIntroShown(self):
        if isExtraIntroVideoEnabled() and not isExtraVideoShown():
            showOverlayVideo(getExtraVideoURL(), callbackOnClose=self.__onExtraVideoShown)

    def __onExtraVideoShown(self):
        setExtraVideoShown()

    def __updateSelectedChapter(self):
        if self.__battlePass.hasExtra() and not isExtraChapterSeen():
            setExtraChapterSeen()
            view = self.__gui.windowsManager.getViewByLayoutID(self.VIEW_KEY.alias)
            if view is not None and getattr(view, 'updateInitialData'):
                view.updateInitialData(selectedChapter=sorted(self.__battlePass.getExtraChapterIDs())[0])
        return


@BattlePassState.parentOf
class ProgressionBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'progression'
    VIEW_KEY = ViewKey(_BP.Progression())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        from gui.impl.lobby.lootbox_system.states import LootBoxMainState
        from gui.impl.lobby.vehicle_hub import OverviewState
        from gui.impl.lobby.vehicle_hub.states import VehicleHubState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        buyPassState = lsm.getStateByCls(BuyPassBattlePassState)
        buyLevelsState = lsm.getStateByCls(BuyLevelsBattlePassState)
        lootBoxMainState = lsm.getStateByCls(LootBoxMainState)
        self.addNavigationTransition(buyPassState)
        self.addNavigationTransition(buyLevelsState)
        self.addNavigationTransition(lsm.getStateByCls(TankmenBattlePassState))
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState))
        self.addNavigationTransition(lootBoxMainState, record=True)
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState))
        lsm.getStateByCls(VehicleHubState).addNavigationTransition(self)


@BattlePassState.parentOf
class PostProgressionBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'postProgression'
    VIEW_KEY = ViewKey(_BP.PostProgression())

    def registerTransitions(self):
        from gui.impl.lobby.lootbox_system.states import LootBoxMainState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        progressionState = lsm.getStateByCls(ProgressionBattlePassState)
        buyPassState = lsm.getStateByCls(BuyPassBattlePassState)
        lootBoxMainState = lsm.getStateByCls(LootBoxMainState)
        self.addNavigationTransition(progressionState)
        self.addNavigationTransition(buyPassState)
        self.addNavigationTransition(lootBoxMainState, record=True)
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)


@BattlePassState.parentOf
class TankmenBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'tankmenScreen'
    VIEW_KEY = ViewKey(_BP.TankmenScreen())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)


@BattlePassState.parentOf
class BuyPassBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyPass'
    VIEW_KEY = ViewKey(_BP.BuyPass())

    def registerTransitions(self):
        lsm = self.getMachine()
        rewardsState = lsm.getStateByCls(BuyPassRewardsBattlePassState)
        self.addNavigationTransition(rewardsState)


@BattlePassState.parentOf
class BuyPassRewardsBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyPassRewards'
    VIEW_KEY = ViewKey(_BP.BuyPassRewards())


@BattlePassState.parentOf
class BuyLevelsBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyLevels'
    VIEW_KEY = ViewKey(_BP.BuyLevels())


@BattlePassState.parentOf
class HolidayFinalBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'holidayFinal'
    VIEW_KEY = ViewKey(_BP.HolidayFinal())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        from gui.impl.lobby.vehicle_hub import OverviewState
        from gui.impl.lobby.vehicle_hub.states import VehicleHubState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(BuyPassBattlePassState))
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState))
        self.addNavigationTransition(lsm.getStateByCls(OverviewState))
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)
        lsm.getStateByCls(VehicleHubState).addNavigationTransition(self)

    @classmethod
    def goTo(cls, **params):
        lobbyStateMachine = getLobbyStateMachine()
        buyPassState = lobbyStateMachine.getStateByCls(BuyPassBattlePassState)
        if buyPassState.isEntered():
            buyPassState.goBack()
        super(HolidayFinalBattlePassState, cls).goTo(**params)


STATES = {_BP.ChapterChoice(): ChapterChoiceBattlePassState,
 _BP.Progression(): ProgressionBattlePassState,
 _BP.PostProgression(): PostProgressionBattlePassState,
 _BP.BuyPass(): BuyPassBattlePassState,
 _BP.BuyPassRewards(): BuyPassRewardsBattlePassState,
 _BP.BuyLevels(): BuyLevelsBattlePassState,
 _BP.HolidayFinal(): HolidayFinalBattlePassState,
 _BP.TankmenScreen(): TankmenBattlePassState}
_INITIAL_STATE_ID = _BP.ChapterChoice()

@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def _shouldNavigateToProgression(event, battlePass=None):
    return not battlePass.isChapterExists(event.params.get('chapterID')) and not battlePass.isHoliday()


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def _isHoliday(event, battlePass=None):
    return battlePass.isHoliday() and not battlePass.isCompleted()


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def _isHolidayComplete(event, battlePass=None):
    return battlePass.isHoliday() and battlePass.isCompleted()
