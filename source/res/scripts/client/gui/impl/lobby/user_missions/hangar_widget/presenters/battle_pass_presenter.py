# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/presenters/battle_pass_presenter.py
from typing import Optional, Set
import BigWorld
from account_helpers.AccountSettings import AccountSettings, IS_BATTLE_PASS_START_ANIMATION_SEEN
from battle_pass_common import getPresentLevel
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.battle_pass_model import AppearAnimationState, BattlePassModel, WidgetState
from gui.impl.lobby.battle_pass.battle_pass_entry_point_view import BaseBattlePassEntryPointView
from gui.impl.lobby.battle_pass.common import isExtraChapterSeen, getExtraChapterID, isUmgExtraChapterSeen
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_no_chapter_tooltip_view import BattlePassNoChapterTooltipView
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showBattlePass
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared.utils import IHangarSpace

class _LastEntryState(object):

    def __init__(self):
        self.rewards = set()
        self.pointsEarned = 0
        self.level = 0
        self.chapterID = 0
        self.rewardsHash = 0

    def update(self, rewards=None, level=0, pointsEarned=0, chapterID=0, rewardsHash=0):
        if rewards is None:
            rewards = set()
        self.rewards = rewards
        self.pointsEarned = pointsEarned
        self.level = level
        self.chapterID = chapterID
        self.rewardsHash = rewardsHash
        return

    def getRewardsHash(self, currentRewards):
        newTokens = currentRewards - self.rewards
        availableTokensLen = len(currentRewards)
        newTokensLen = len(newTokens)
        if availableTokensLen == 0:
            return 0
        return self.rewardsHash if newTokensLen == 0 else self.rewardsHash + 1


_SPACE_CREATED_UPDATE_DELAY = 0.7
_g_entryLastState = _LastEntryState()

class BattlePassPresenter(TooltipPositionerMixin, OverlapCtrlMixin, ViewComponent[BattlePassModel], BaseBattlePassEntryPointView):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        self._firstUpdatePerformed = False
        self._readyForAnimations = self.__hangarSpace.spaceInited
        super(BattlePassPresenter, self).__init__(model=BattlePassModel)

    @property
    def viewModel(self):
        return super(BattlePassPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if not self.isHoliday and contentID == R.views.lobby.battle_pass.tooltips.BattlePassNoChapterTooltipView():
            return BattlePassNoChapterTooltipView()
        return BattlePassCompletedTooltipView() if contentID == R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView() else BattlePassInProgressTooltipView()

    @property
    def hasDeferModelUpdate(self):
        isDeferUpdate = super(BattlePassPresenter, self).hasDeferModelUpdate
        isSpaceInited = self.__hangarSpace.spaceInited
        return isDeferUpdate or not isSpaceInited

    @staticmethod
    def _onIntroAnimationPlayed():
        AccountSettings.setSettings(IS_BATTLE_PASS_START_ANIMATION_SEEN, True)

    @staticmethod
    def _isIntroAnimationPlayed():
        return AccountSettings.getSettings(IS_BATTLE_PASS_START_ANIMATION_SEEN)

    def _getEvents(self):
        return super(BattlePassPresenter, self)._getEvents() + ((self.viewModel.onOpenBattlePass, self._onClick), (self.viewModel.onIntroAnimationPlayed, self._onIntroAnimationPlayed), (self.__hangarSpace.onSpaceCreate, self._onSpaceCreate))

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(BattlePassPresenter, self)._onLoading(*args, **kwargs)
        self._start()

    def _onClick(self):
        showBattlePass()

    def _onPointsUpdated(self, *_):
        self._updateOptional()

    def _onOffersUpdated(self, *_):
        if not self.__battlePass.isDisabled():
            self._updateOptional()

    def _delayedUpdateAfterSpaceCreated(self):
        if self._isFinalized:
            return
        self._readyForAnimations = True
        self._preInitModel()
        self._updateData()

    def _onSpaceCreate(self):
        if self._isFinalized:
            return
        BigWorld.callback(_SPACE_CREATED_UPDATE_DELAY, self._delayedUpdateAfterSpaceCreated)

    def _finalize(self):
        self._stop()
        if self._firstUpdatePerformed:
            self._savePresenterLastState()
        super(BattlePassPresenter, self)._finalize()

    def _updateOptional(self):
        if not self.__battlePass.isDisabled():
            hasRareLevel = any((self.__battlePass.isRareLevel(self.chapterID, lvl) for lvl in range(_g_entryLastState.level + 1, self.level + 1)))
            if not hasRareLevel:
                self._updateData()

    def _updateData(self, *_):
        if not self.isUpdateQueued:
            self.deferUpdate(self._updateViewModel)
        self._updateViewModelIfNeeded()

    def _rawUpdate(self):
        super(BattlePassPresenter, self)._rawUpdate()
        with self.viewModel.transaction() as tx:
            self._fillViewModel(tx)

    def _updateViewModel(self):
        self.queueUpdate()

    def _preInitModel(self):
        points, limit = self.__battlePass.getLevelProgression(self.chapterID)
        _g_entryLastState.update(level=self.level, pointsEarned=points, chapterID=self.chapterID)
        chapterID = self.chapterID
        level = getPresentLevel(self.level)
        with self.viewModel.transaction() as tx:
            self._fillModel(tx, chapterID, points, limit, level, 0)
            tx.lastSeenState.setPointsEarned(points)
            tx.lastSeenState.setLevel(level)

    def _fillViewModel(self, tx):
        self._firstUpdatePerformed = True
        chapterID = self.chapterID
        points, limit = self.__battlePass.getLevelProgression(chapterID)
        level = getPresentLevel(self.level)
        rewards = set(self.__battlePass.getNotChosenRewardsIter())
        rewardsHash = _g_entryLastState.getRewardsHash(rewards)
        self._fillModel(tx, chapterID, points, limit, level, rewardsHash)
        self._fillLastSeen(tx, chapterID, points, level, rewards, rewardsHash)

    def _fillModel(self, tx, chapterID, points, limit, level, rewardsHash):
        extraChapterId = getExtraChapterID()
        isBattlePassExtraChapterSeen = isExtraChapterSeen()
        tx.setWidgetState(self._getWidgetState(isBattlePassExtraChapterSeen))
        tx.setLevel(level)
        tx.setTooltipID(self._getTooltip())
        tx.setChapterID(chapterID)
        tx.setSeason(self.__battlePass.getSeasonNum())
        tx.setIsBought(self.isBought)
        tx.setIsPaused(self.isPaused)
        tx.setIsExtraChapter(self.__battlePass.isExtraChapter(chapterID))
        tx.setRewardsHash(rewardsHash)
        tx.setHasExtraChapter(self._hasExtraChapter(extraChapterId))
        tx.setIsExtraChapterHighlighted(self._needToShowExtraIntro(isBattlePassExtraChapterSeen))
        tx.setAppearAnimationState(self._getAppearAnimationState())
        extraTimeLeft = self.__battlePass.getChapterRemainingTime(extraChapterId)
        timeLeft = self.__battlePass.getSeasonTimeLeft()
        if chapterID:
            tx.setTimeLeft(extraTimeLeft if self.__battlePass.isExtraChapter(chapterID) else timeLeft)
        else:
            tx.setTimeLeft(extraTimeLeft if self.__battlePass.hasExtra() else timeLeft)
        tx.setPointsEarned(points)
        tx.setLevelPoints(limit)

    def _fillLastSeen(self, tx, chapterID, points, level, rewards, rewardsHash):
        if _g_entryLastState.chapterID == chapterID:
            tx.lastSeenState.setPointsEarned(_g_entryLastState.pointsEarned)
            tx.lastSeenState.setLevel(getPresentLevel(_g_entryLastState.level))
        else:
            tx.lastSeenState.setPointsEarned(points)
            tx.lastSeenState.setLevel(level)
        tx.lastSeenState.setRewardsHash(_g_entryLastState.rewardsHash)
        self._savePresenterLastState(rewards=rewards, rewardsHash=rewardsHash)

    def _needToShowExtraIntro(self, isBattlePassExtraChapterSeen):
        return self.hasExtra and (not isBattlePassExtraChapterSeen or self.isPostProgressionActive and not isUmgExtraChapterSeen())

    def _getAppearAnimationState(self):
        if self._isIntroAnimationPlayed():
            return AppearAnimationState.PLAYED
        return AppearAnimationState.READY if not self.hasDeferModelUpdate and self._readyForAnimations else AppearAnimationState.WAITING

    def _getWidgetState(self, isBattlePassExtraChapterSeen):
        if self.isCompleted and not self.isPostProgressionActive:
            return WidgetState.COMPLETED
        isIntro = not bool(self.chapterID) or self._needToShowExtraIntro(isBattlePassExtraChapterSeen)
        return WidgetState.INTRO if isIntro else WidgetState.PROGRESSION

    def _hasExtraChapter(self, chapterID):
        return self.hasExtra and self.__battlePass.getChapterState(chapterID) != ChapterState.COMPLETED

    def _savePresenterLastState(self, rewards=None, rewardsHash=None):
        points, _ = self.__battlePass.getLevelProgression(self.chapterID)
        if rewards is None:
            rewards = set(self.__battlePass.getNotChosenRewardsIter())
        if rewardsHash is None:
            rewardsHash = _g_entryLastState.getRewardsHash(rewards)
        _g_entryLastState.update(rewards=rewards, level=self.level, pointsEarned=points, chapterID=self.chapterID, rewardsHash=rewardsHash)
        return
