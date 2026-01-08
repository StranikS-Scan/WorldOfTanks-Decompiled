# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/states.py
from typing import TYPE_CHECKING
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_pass.battle_pass_helpers import getExtraVideoURL, getIntroVideoURL
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.battle_pass.common import isExtraChapterSeen, isExtraVideoShown, isIntroShown, isIntroVideoShown, setExtraChapterSeen, setExtraVideoShown, setIntroVideoShown, showOverlayVideo
from gui.lobby_state_machine.states import LobbyState, LobbyStateDescription, SubScopeSubLayerState, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.shared.event_dispatcher import showBattlePass
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import IBattlePassController
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
        for state in childStates.itervalues():
            lsm.addState(state())

    def registerTransitions(self):
        lsm = self.getMachine()
        for state in self.getChildrenStates():
            lsm.addNavigationTransitionFromParent(state)

        introVideoState = lsm.getStateByCls(IntroVideoBattlePassState)
        self.addTransition(HijackTransition(IntroBattlePassState, _shouldNavigateToIntroVideo), introVideoState)
        extraVideoState = lsm.getStateByCls(ExtraVideoBattlePassState)
        self.addTransition(HijackTransition(IntroBattlePassState, _shouldNavigateToExtraVideo), extraVideoState)
        progressionState = lsm.getStateByCls(ProgressionBattlePassState)
        self.addTransition(HijackTransition(ChapterChoiceBattlePassState, _isHoliday), progressionState)

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
        shortStateID = self.STATE_ID.split('/')[-1]
        return LobbyStateDescription(title=backport.text(R.strings.battle_pass.navigation.dyn(shortStateID)(), **self._getNavigationDescriptionArgs()))

    def _getNavigationDescriptionArgs(self):
        return {}

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(_BattlePassPresenterState, self)._onEntered(event)

    def _onExited(self):
        super(_BattlePassPresenterState, self)._onExited()
        self.__cachedParams = {}


@BattlePassState.parentOf
class IntroVideoBattlePassState(LobbyState):
    STATE_ID = 'introVideo'
    VIEW_KEY = ViewKey(_BP.IntroVideo())

    def _onEntered(self, event):
        super(IntroVideoBattlePassState, self)._onEntered(event)
        self.__showOverlayVideo()

    @nextTick
    def __showOverlayVideo(self):
        showOverlayVideo(getIntroVideoURL(), self.__onVideoShown)

    @staticmethod
    def __onVideoShown():
        setIntroVideoShown()
        IntroBattlePassState.goTo()


@BattlePassState.parentOf
class ExtraVideoBattlePassState(LobbyState):
    STATE_ID = 'extraVideo'
    VIEW_KEY = ViewKey(_BP.ExtraVideo())

    def _onEntered(self, event):
        super(ExtraVideoBattlePassState, self)._onEntered(event)
        self.__showOverlayVideo()

    @nextTick
    def __showOverlayVideo(self):
        showOverlayVideo(getExtraVideoURL(), self.__onVideoShown)

    @staticmethod
    def __onVideoShown():
        setExtraVideoShown()
        IntroBattlePassState.goTo()


@BattlePassState.parentOf
class IntroBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'intro'
    VIEW_KEY = ViewKey(_BP.Intro())
    __battlePass = dependency.descriptor(IBattlePassController)

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)

    def _getNavigationDescriptionArgs(self):
        return {'seasonNum': self.__battlePass.getSeasonNum()}

    def _onEntered(self, event):
        if self.__needShowIntroVideo():
            IntroVideoBattlePassState.goTo(**event.params)
        elif self.__needShowIntroView():
            super(IntroBattlePassState, self)._onEntered(event)
        elif self.__battlePass.hasExtra() and not isExtraChapterSeen():
            setExtraChapterSeen()
            showBattlePass(_BP.ChapterChoice())
        else:
            showBattlePass(**event.params)

    def __needShowIntroView(self):
        return not isIntroShown()

    def __needShowIntroVideo(self):
        return not isIntroVideoShown() or not isExtraVideoShown()


@BattlePassState.parentOf
class ChapterChoiceBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'chapterChoice'
    VIEW_KEY = ViewKey(_BP.ChapterChoice())
    __battlePass = dependency.descriptor(IBattlePassController)

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        progressionState = lsm.getStateByCls(ProgressionBattlePassState)
        postProgressionState = lsm.getStateByCls(PostProgressionBattlePassState)
        self.addNavigationTransition(progressionState)
        self.addNavigationTransition(postProgressionState)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)

    def _getNavigationDescriptionArgs(self):
        return {'seasonNum': self.__battlePass.getSeasonNum()}


@BattlePassState.parentOf
class ProgressionBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'progression'
    VIEW_KEY = ViewKey(_BP.Progression())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        from gui.impl.lobby.lootbox_system.states import LootBoxMainState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        buyPassState = lsm.getStateByCls(BuyPassBattlePassState)
        buyPassConfirmState = lsm.getStateByCls(BuyPassConfirmBattlePassState)
        buyLevelsState = lsm.getStateByCls(BuyLevelsBattlePassState)
        lootBoxMainState = lsm.getStateByCls(LootBoxMainState)
        self.addNavigationTransition(buyPassState)
        self.addNavigationTransition(buyPassConfirmState)
        self.addNavigationTransition(buyLevelsState)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState))
        self.addNavigationTransition(lootBoxMainState, record=True)
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)


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
        buyPassConfirmState = lsm.getStateByCls(BuyPassConfirmBattlePassState)
        lootBoxMainState = lsm.getStateByCls(LootBoxMainState)
        self.addNavigationTransition(progressionState)
        self.addNavigationTransition(buyPassState)
        self.addNavigationTransition(buyPassConfirmState)
        self.addNavigationTransition(lootBoxMainState, record=True)
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)


@BattlePassState.parentOf
class BuyPassBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyPass'
    VIEW_KEY = ViewKey(_BP.BuyPass())

    def registerTransitions(self):
        lsm = self.getMachine()
        confirmState = lsm.getStateByCls(BuyPassConfirmBattlePassState)
        self.addNavigationTransition(confirmState)


@BattlePassState.parentOf
class BuyPassConfirmBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyPassConfirm'
    VIEW_KEY = ViewKey(_BP.BuyPassConfirm())

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

    def registerTransitions(self):
        lsm = self.getMachine()
        rewardsState = lsm.getStateByCls(BuyLevelsRewardsBattlePassState)
        self.addNavigationTransition(rewardsState)


@BattlePassState.parentOf
class BuyLevelsRewardsBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyLevelsRewards'
    VIEW_KEY = ViewKey(_BP.BuyLevelsRewards())


@BattlePassState.parentOf
class HolidayFinalBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'holidayFinal'
    VIEW_KEY = ViewKey(_BP.HolidayFinal())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import ConfigurableVehiclePreviewState
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StyleProgressionPreviewState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        confirmState = lsm.getStateByCls(BuyPassConfirmBattlePassState)
        rewardsState = lsm.getStateByCls(BuyPassRewardsBattlePassState)
        self.addNavigationTransition(confirmState)
        self.addNavigationTransition(rewardsState)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ConfigurableVehiclePreviewState))
        self.addNavigationTransition(lsm.getStateByCls(StyleProgressionPreviewState))
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)


STATES = {_BP.IntroVideo(): IntroVideoBattlePassState,
 _BP.ExtraVideo(): ExtraVideoBattlePassState,
 _BP.Intro(): IntroBattlePassState,
 _BP.ChapterChoice(): ChapterChoiceBattlePassState,
 _BP.Progression(): ProgressionBattlePassState,
 _BP.PostProgression(): PostProgressionBattlePassState,
 _BP.BuyPass(): BuyPassBattlePassState,
 _BP.BuyPassConfirm(): BuyPassConfirmBattlePassState,
 _BP.BuyPassRewards(): BuyPassRewardsBattlePassState,
 _BP.BuyLevels(): BuyLevelsBattlePassState,
 _BP.BuyLevelsRewards(): BuyLevelsRewardsBattlePassState,
 _BP.HolidayFinal(): HolidayFinalBattlePassState}
_INITIAL_STATE_ID = _BP.Intro()

def _shouldNavigateToIntroVideo(event):
    return not isIntroVideoShown()


def _shouldNavigateToExtraVideo(event):
    return isIntroVideoShown() and not isExtraVideoShown()


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def _isHoliday(event, battlePass=None):
    return battlePass.isHoliday()
