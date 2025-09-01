# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/main_view.py
import logging
from typing import TYPE_CHECKING
import Event
from frameworks.state_machine import BaseStateObserver, StateEvent, visitor
from frameworks.wulf import WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.sounds import BATTLE_PASS_TASKS_SOUND_SPACE, BattlePassSounds, switchDialogBPSoundFilter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.main_view_model import MainViewModel
from gui.impl.lobby.battle_pass.battle_pass_buy_levels_view import BuyLevelsPresenter
from gui.impl.lobby.battle_pass.battle_pass_buy_view import BuyPassPresenter
from gui.impl.lobby.battle_pass.battle_pass_progressions_view import ProgressionPresenter
from gui.impl.lobby.battle_pass.chapter_choice_view import ChapterChoicePresenter
from gui.impl.lobby.battle_pass.holiday_final_view import HolidayFinalPresenter
from gui.impl.lobby.battle_pass.intro_view import IntroPresenter
from gui.impl.lobby.battle_pass.post_progression_view import PostProgressionPresenter
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.shared.event_dispatcher import showHangar
from gui.sounds.ambients import BattlePassSoundEnv
from helpers import dependency
from shared_utils import safeCall
from skeletons.gui.game_control import IBattlePassController
if TYPE_CHECKING:
    from typing import Optional
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.lobby_state_machine.states import LobbyState
_logger = logging.getLogger(__name__)
_BP = R.aliases.battle_pass
_PRESENTERS = {_BP.Intro(): IntroPresenter,
 _BP.ChapterChoice(): ChapterChoicePresenter,
 _BP.Progression(): ProgressionPresenter,
 _BP.PostProgression(): PostProgressionPresenter,
 _BP.BuyPass(): BuyPassPresenter,
 _BP.BuyLevels(): BuyLevelsPresenter,
 _BP.HolidayFinal(): HolidayFinalPresenter}
_PARENTS = {_BP.BuyPassConfirm(): _BP.BuyPass(),
 _BP.BuyPassRewards(): _BP.BuyPass(),
 _BP.BuyLevelsRewards(): _BP.BuyLevels()}
_UNTRACKED = frozenset((_BP.IntroVideo(), _BP.ExtraVideo(), _BP.FinalRewardPreview()))

class _BattlePassStatesObserver(BaseStateObserver):

    def __init__(self):
        super(_BattlePassStatesObserver, self).__init__()
        self.onSubViewSelect = Event.Event()

    def clear(self):
        super(_BattlePassStatesObserver, self).clear()
        self.onSubViewSelect.clear()

    def isObservingState(self, state):
        from gui.impl.lobby.battle_pass.states import BattlePassState
        return visitor.isDescendantOf(state, state.getMachine().getStateByCls(BattlePassState)) and state.VIEW_KEY.alias not in _UNTRACKED

    def onEnterState(self, state, event):
        self.onSubViewSelect(state.VIEW_KEY.alias, **event.params)


class MainView(ViewComponent[MainViewModel], IRoutableView):
    _COMMON_SOUND_SPACE = BATTLE_PASS_TASKS_SOUND_SPACE
    __sound_env__ = BattlePassSoundEnv
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, *args, **kwargs):
        super(MainView, self).__init__(R.views.lobby.battle_pass.MainView(), MainViewModel)
        self.__lsm = None
        self.__router = None
        self.__statesObserver = _BattlePassStatesObserver()
        self.__activePresenterID = None
        self.__activeChapterID = None
        return

    @property
    def viewModel(self):
        return super(MainView, self).getViewModel()

    def getRouterModel(self):
        return self.viewModel.router

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(MainView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(MainView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__safeCallOnActivePresenter('getTooltipData', event)

    def _onLoading(self, *args, **kwargs):
        from gui.impl.lobby.battle_pass.states import BattlePassState
        self.__lsm = getLobbyStateMachine()
        self.__lsm.connect(self.__statesObserver)
        self.__router = SubstateRouter(self.__lsm, self, self.__lsm.getStateByCls(BattlePassState))
        self.__router.init()
        self.soundManager.playSound(BattlePassSounds.TASKS_ENTER)
        super(MainView, self)._onLoading(**kwargs)

    def _finalize(self):
        super(MainView, self)._finalize()
        self.__playExitSounds()
        self.__router.fini()
        self.__router = None
        self.__lsm.disconnect(self.__statesObserver)
        self.__lsm = None
        self.__statesObserver.clear()
        self.__statesObserver = None
        return

    def _getEvents(self):
        return ((self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassSettingsChanged),
         (self.__battlePass.onExtraChapterExpired, self.__onExtraChapterExpired),
         (self.__statesObserver.onSubViewSelect, self.__switchSubView))

    def __onBattlePassSettingsChanged(self, *_):
        if not (self.__battlePass.isEnabled() and self.__battlePass.isActive()):
            showHangar()

    def __onExtraChapterExpired(self):
        self.__safeCallOnActivePresenter('onExtraChapterExpired')

    def __switchSubView(self, presenterID, **kwargs):
        if self.__activePresenterID in self._childrenUidByPosition:
            self.__safeCallOnActivePresenter('deactivate')
        kwargs['originStateID'] = self.__activePresenterID
        kwargs['childStateID'] = presenterID
        self.__activePresenterID = _PARENTS.get(presenterID, presenterID)
        self.__updateActiveChapterID(**kwargs)
        if self.__activePresenterID not in self._childrenUidByPosition:
            self._registerChild(self.__activePresenterID, _PRESENTERS[self.__activePresenterID](**kwargs))
        else:
            self.__safeCallOnActivePresenter('updateInitialData', **kwargs)
            self.__safeCallOnActivePresenter('activate')
        self.__playSwitchSounds(kwargs.get('originStateID'), kwargs.get('chapterID'))

    def __updateActiveChapterID(self, **kwargs):
        if 'chapterID' in kwargs and kwargs['chapterID']:
            self.__activeChapterID = kwargs['chapterID']

    def __safeCallOnActivePresenter(self, methodName, *args, **kwargs):
        return safeCall(getattr(self._childrenByUid[self._childrenUidByPosition[self.__activePresenterID]], methodName, None), *args, **kwargs)

    def __playSwitchSounds(self, originalPresenterID, previousChapter):
        switchDialogBPSoundFilter(self.__activePresenterID in (_BP.BuyPass(), _BP.BuyLevels()))
        if self.__activePresenterID not in (_BP.ChapterChoice(), _BP.Progression(), _BP.PostProgression()) or originalPresenterID in (_BP.BuyPass(), _BP.BuyLevels()) and self.__activePresenterID == _BP.Progression():
            return
        if self.__isExtraChapterProgression():
            if self.soundManager.isSoundPlaying(BattlePassSounds.TASKS_ENTER):
                self.soundManager.stopSound(BattlePassSounds.TASKS_ENTER)
                self.soundManager.playSound(BattlePassSounds.TASKS_EXIT)
            if not self.soundManager.isSoundPlaying(BattlePassSounds.SPECIAL_TASKS_ENTER):
                self.soundManager.playSound(BattlePassSounds.SPECIAL_TASKS_ENTER)
        else:
            if self.soundManager.isSoundPlaying(BattlePassSounds.SPECIAL_TASKS_ENTER) or bool(self.__activeChapterID) and previousChapter != self.__activeChapterID and self.__battlePass.isExtraChapter(self.__activeChapterID):
                self.soundManager.stopSound(BattlePassSounds.SPECIAL_TASKS_ENTER)
                self.soundManager.playSound(BattlePassSounds.SPECIAL_TASKS_EXIT)
            if not self.soundManager.isSoundPlaying(BattlePassSounds.TASKS_ENTER):
                self.soundManager.playSound(BattlePassSounds.TASKS_ENTER)

    def __playExitSounds(self):
        if self.__isExtraChapterProgression() or self.soundManager.isSoundPlaying(BattlePassSounds.SPECIAL_TASKS_ENTER):
            self.soundManager.stopSound(BattlePassSounds.SPECIAL_TASKS_ENTER)
            self.soundManager.playSound(BattlePassSounds.SPECIAL_TASKS_EXIT)
        else:
            self.soundManager.stopSound(BattlePassSounds.TASKS_ENTER)
            self.soundManager.playSound(BattlePassSounds.TASKS_EXIT)
        switchDialogBPSoundFilter(False)

    def __isExtraChapterProgression(self):
        return self.__activePresenterID == _BP.Progression() and self.__battlePass.isExtraChapter(self.__activeChapterID)


class BattlePassWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(BattlePassWindow, self).__init__(content=MainView(), wndFlags=WindowFlags.WINDOW, layer=layer)
