# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/states.py
import typing
from WeakMethod import WeakMethodProxy
from battle_royale.gui.shared.event_dispatcher import showInfoPage
from battle_royale.skeletons.game_controller import IBRProgressionOnTokensController
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.battle_results.service import PostBattleResultsStateMixin
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SubScopeSubLayerState, LobbyStateFlags, SFViewLobbyState, LobbyState, LobbyStateDescription, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.shared.utils.functions import getViewName
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
if typing.TYPE_CHECKING:
    from typing import Optional

def registerStates(lsm):
    lsm.addState(BattleRoyaleModeState())


def registerTransitions(lsm):
    battleRoyaleMode = lsm.getStateByCls(BattleRoyaleModeState)
    lsm.addNavigationTransitionFromParent(battleRoyaleMode)


@SubScopeSubLayerState.parentOf
class BattleRoyaleModeState(LobbyState):
    STATE_ID = 'battleRoyale'
    battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(BattleRoyaleHangarState(LobbyStateFlags.INITIAL))
        machine.addState(BattleRoyaleTournamentQueueState())
        machine.addState(BattleRoyaleProgressionState())
        machine.addState(BattleRoyaleBattleResultsState())
        machine.addState(BattleRoyalePrimeTimeState())
        machine.addState(BattleRoyaleVehicleInfoState())

    def registerTransitions(self):
        from gui.impl.lobby.hangar.states import HangarState
        lsm = self.getMachine()
        parent = self.getParent()
        hangar = lsm.getStateByCls(BattleRoyaleHangarState)
        parent.addNavigationTransition(hangar, record=True)
        parent.addTransition(HijackTransition(HangarState, WeakMethodProxy(self._isBattleRoyaleMode)), hangar)
        battleResultsState = lsm.getStateByCls(BattleRoyaleBattleResultsState)
        tournamentQueue = lsm.getStateByCls(BattleRoyaleTournamentQueueState)
        battleResultsState.addNavigationTransition(tournamentQueue, TransitionType.EXTERNAL)
        parent.addNavigationTransition(battleResultsState)
        progressionState = lsm.getStateByCls(BattleRoyaleProgressionState)
        parent.addNavigationTransition(progressionState)
        for cls in (BattleRoyalePrimeTimeState, BattleRoyaleVehicleInfoState, BattleRoyaleTournamentQueueState):
            state = lsm.getStateByCls(cls)
            hangar.addNavigationTransition(state)

    @classmethod
    def _isBattleRoyaleMode(cls, event):
        return cls.battleRoyaleController.isBattleRoyaleMode()


@BattleRoyaleModeState.parentOf
class BattleRoyaleHangarState(ViewLobbyState):
    STATE_ID = 'battleRoyaleHangar'
    VIEW_KEY = ViewKey(BATTLEROYALE_ALIASES.BR_HANGAR_VIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(BattleRoyaleHangarState, self).__init__(flags | LobbyStateFlags.HANGAR)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.mode_selector.mode.battleRoyaleQueue.title()))


@BattleRoyaleModeState.parentOf
class BattleRoyaleTournamentQueueState(ViewLobbyState):
    STATE_ID = 'battleRoyaleTournamentBattleQueue'
    VIEW_KEY = ViewKey(BATTLEROYALE_ALIASES.BR_TOURNAMENT_BATTLE_QUEUE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.waiting.prebattle.battle_queue()))


@BattleRoyaleModeState.parentOf
class BattleRoyaleProgressionState(ViewLobbyState):
    battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    STATE_ID = 'battleRoyaleProgression'
    VIEW_KEY = ViewKey(BATTLEROYALE_ALIASES.BR_PROGRESSION)
    NAVIGATION_BUTTONS = (LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showInfoPage),)

    def _onExited(self):
        brProgression = dependency.instance(IBRProgressionOnTokensController)
        brProgression.saveCurPoints()
        super(BattleRoyaleProgressionState, self)._onExited()

    def getNavigationDescription(self):
        if self.battleRoyaleController.isStPatrick():
            text = R.strings.pages.titles.battleRoyale.stPatrick.progression()
        else:
            text = R.strings.pages.titles.battleRoyale.progression()
        return LobbyStateDescription(title=backport.text(text), infos=self.NAVIGATION_BUTTONS)


@BattleRoyaleModeState.parentOf
class BattleRoyaleBattleResultsState(ViewLobbyState, PostBattleResultsStateMixin):
    STATE_ID = BATTLEROYALE_ALIASES.BR_BATTLE_RESULTS
    VIEW_KEY = ViewKey(BATTLEROYALE_ALIASES.BR_BATTLE_RESULTS)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(BattleRoyaleBattleResultsState, self).__init__(flags=flags | LobbyStateFlags.POST_BATTLE_RESULTS)
        self.__cachedParams = {}

    def getViewKey(self, params=None):
        arenaUniqueID = self.__cachedParams.get('arenaUniqueID', '')
        alias = super(BattleRoyaleBattleResultsState, self).getViewKey().alias
        return ViewKey(alias, getViewName(alias, arenaUniqueID))

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battleRoyale.battle_results()))

    def registerTransitions(self):
        machine = self.getMachine()
        machine.addNavigationTransitionFromParent(self)
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        self.__cachedParams = dict(event.params)
        super(BattleRoyaleBattleResultsState, self)._onEntered(event)

    def _onExited(self):
        super(BattleRoyaleBattleResultsState, self)._onExited()
        self.__cachedParams = {}


@BattleRoyaleModeState.parentOf
class BattleRoyalePrimeTimeState(SFViewLobbyState):
    STATE_ID = 'battleRoyalePrimeTime'
    VIEW_KEY = ViewKey(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battleRoyale.primeTime()))


@BattleRoyaleModeState.parentOf
class BattleRoyaleVehicleInfoState(SFViewLobbyState):
    STATE_ID = 'battleRoyaleVehicleInfo'
    VIEW_KEY = ViewKey(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battleRoyale.upgrades()))
