# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/main_view.py
from __future__ import absolute_import
import logging
from typing import TYPE_CHECKING
import Event
from frameworks.state_machine import BaseStateObserver, StateEvent, visitor
from frameworks.wulf import WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import getChapterForTankmenScreen
from gui.battle_pass.sounds import BATTLE_PASS_TASKS_SOUND_SPACE, switchBattlePassSoundFilter, getBattlePassEnterSound, getBattlePassExitSound, getBattlePassExtraExitSound, getBattlePassExtraEnterSound, switchOverlaySoundFilter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.main_view_model import MainViewModel
from gui.impl.lobby.battle_pass.battle_pass_buy_levels_view import BuyLevelsPresenter
from gui.impl.lobby.battle_pass.battle_pass_buy_view import BuyPassPresenter
from gui.impl.lobby.battle_pass.battle_pass_progressions_view import ProgressionPresenter
from gui.impl.lobby.battle_pass.chapter_choice_view import ChapterChoicePresenter
from gui.impl.lobby.battle_pass.holiday_final_view import HolidayFinalPresenter
from gui.impl.lobby.battle_pass.post_progression_view import PostProgressionPresenter
from gui.impl.lobby.battle_pass.tankmen_voiceover_view import TankmenVoiceoverPresenter
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from shared_utils import safeCall
from skeletons.gui.game_control import IBattlePassController
if TYPE_CHECKING:
    from typing import Optional
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.lobby_state_machine.states import LobbyState
_logger = logging.getLogger(__name__)
_BP = R.aliases.battle_pass
_PRESENTERS = {_BP.ChapterChoice(): ChapterChoicePresenter,
 _BP.Progression(): ProgressionPresenter,
 _BP.PostProgression(): PostProgressionPresenter,
 _BP.BuyPass(): BuyPassPresenter,
 _BP.BuyLevels(): BuyLevelsPresenter,
 _BP.HolidayFinal(): HolidayFinalPresenter,
 _BP.TankmenScreen(): TankmenVoiceoverPresenter}
_PARENTS = {_BP.BuyPassRewards(): _BP.BuyPass()}
_UNTRACKED = frozenset((_BP.FinalRewardPreview(),))
_NO_CHAPTER_PRESENTERS = frozenset((_BP.ChapterChoice(), _BP.PostProgression()))

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
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, *args, **kwargs):
        super(MainView, self).__init__(R.views.mono.battle_pass.main(), MainViewModel)
        self.__lsm = None
        self.__router = None
        self.__statesObserver = _BattlePassStatesObserver()
        self.__activePresenterID = None
        self.__activeChapterID = None
        self.__selectedChapter = None
        return

    @property
    def viewModel(self):
        return super(MainView, self).getViewModel()

    @property
    def selectedChapter(self):
        return self.__selectedChapter

    def updateSelectedChapter(self, chapterID):
        self.__selectedChapter = chapterID

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
        self.__playEnterSounds()
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
        return ((self.__battlePass.onBattlePassSettingsChange, self.__onSettingsChanged),
         (self.__battlePass.onSeasonStateChanged, self.__onSettingsChanged),
         (self.__battlePass.onExtraChapterExpired, self.__onExtraChapterExpired),
         (self.__statesObserver.onSubViewSelect, self.__switchSubView))

    def __onSettingsChanged(self, *_):
        if not (self.__battlePass.isEnabled() and self.__battlePass.isActive()) or self.__battlePass.isPaused():
            showHangar()

    def __onExtraChapterExpired(self):
        self.__safeCallOnActivePresenter('onExtraChapterExpired')

    def __switchSubView(self, presenterID, **kwargs):
        parentPresenterID = _PARENTS.get(presenterID, presenterID)
        if self.__activePresenterID in self._childrenUidByPosition and self.__activePresenterID != parentPresenterID:
            self.__safeCallOnActivePresenter('deactivate')
        kwargs['originStateID'] = self.__activePresenterID
        kwargs['childStateID'] = presenterID
        self.__activePresenterID = parentPresenterID
        self.__selectedChapter = kwargs.get('selectedChapter', 0)
        previousChapter = self.__activeChapterID
        if 'chapterID' in kwargs and kwargs['chapterID']:
            self.__activeChapterID = kwargs['chapterID']
        elif 'screenID' in kwargs:
            chapter = getChapterForTankmenScreen(kwargs['screenID'])
            if chapter is not None:
                self.__activeChapterID = chapter
        if self.__activePresenterID not in self._childrenUidByPosition:
            self._registerChild(self.__activePresenterID, _PRESENTERS[self.__activePresenterID](**kwargs))
        else:
            self.__safeCallOnActivePresenter('updateInitialData', **kwargs)
            if self.__activePresenterID != kwargs['originStateID']:
                self.__safeCallOnActivePresenter('activate')
        self.__playSwitchSounds(kwargs.get('originStateID'), previousChapter)
        return

    def __safeCallOnActivePresenter(self, methodName, *args, **kwargs):
        return safeCall(getattr(self._childrenByUid[self._childrenUidByPosition[self.__activePresenterID]], methodName, None), *args, **kwargs)

    def __playEnterSounds(self):
        self.soundManager.startSpace(BATTLE_PASS_TASKS_SOUND_SPACE)
        self.soundManager.playSound(getBattlePassEnterSound(battlePass=self.__battlePass))

    def __playSwitchSounds(self, originalPresenterID, previousChapter):
        switchOverlaySoundFilter(self.__activePresenterID in (_BP.BuyPass(), _BP.BuyLevels()))
        includedActivePresenters = (_BP.ChapterChoice(),
         _BP.Progression(),
         _BP.PostProgression(),
         _BP.TankmenScreen())
        sameChapterTransition = previousChapter == self.__activeChapterID and (originalPresenterID in (_BP.BuyPass(), _BP.BuyLevels(), _BP.TankmenScreen()) and self.__activePresenterID == _BP.Progression() or originalPresenterID == _BP.Progression() and self.__activePresenterID == _BP.TankmenScreen())
        if self.__battlePass.isHoliday() or self.__activePresenterID not in includedActivePresenters or sameChapterTransition:
            return
        if self.__isExtraChapterPresenter():
            extraEnterSound = getBattlePassExtraEnterSound(self.__activeChapterID)
            self.soundManager.stopSound(extraEnterSound)
            self.soundManager.playSound(extraEnterSound)
            switchBattlePassSoundFilter(on=False)
        elif (previousChapter != self.__activeChapterID or self.__activePresenterID in _NO_CHAPTER_PRESENTERS) and originalPresenterID not in _NO_CHAPTER_PRESENTERS and self.__battlePass.isExtraChapter(previousChapter):
            self.soundManager.playSound(getBattlePassExtraExitSound(previousChapter))
            switchBattlePassSoundFilter(on=True)

    def __playExitSounds(self):
        if self.__isExtraChapterPresenter():
            self.soundManager.playSound(getBattlePassExtraExitSound(self.__activeChapterID))
        self.soundManager.playSound(getBattlePassExitSound(battlePass=self.__battlePass))
        switchOverlaySoundFilter(on=False)

    def __isExtraChapterPresenter(self):
        return self.__activePresenterID not in _NO_CHAPTER_PRESENTERS and self.__battlePass.isExtraChapter(self.__activeChapterID)


class BattlePassWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(BattlePassWindow, self).__init__(content=MainView(), wndFlags=WindowFlags.WINDOW, layer=layer)
