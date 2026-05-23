# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_entry_point_view.py
from __future__ import absolute_import
from battle_pass_common import CurrencyBP, isPostProgressionChapter
from gui.battle_pass.battle_pass_helpers import getSupportedCurrentArenaBonusType
from gui.impl.gen import R
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showBattlePass
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
FULL_PROGRESS = 100

class BaseBattlePassEntryPointView(IGlobalListener, EventsHandler):
    __battlePass = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(BaseBattlePassEntryPointView, self).__init__()

    @property
    def chapterID(self):
        return self.__battlePass.getHolidayChapterID() if self.__battlePass.isHoliday() else self.__battlePass.getCurrentChapterID()

    @property
    def seasonNum(self):
        return self.__battlePass.getSeasonNum()

    @property
    def level(self):
        return self.__battlePass.getCurrentLevelWithPostProgress()

    @property
    def currentLevel(self):
        return self.__battlePass.getCurrentLevel()

    @property
    def isChapterChosen(self):
        return self.__battlePass.hasActiveChapter()

    @property
    def cycle(self):
        return self.__battlePass.getCompletedCyclesCount(self.chapterID)

    @property
    def isBought(self):
        chapterID = self.chapterID
        if isPostProgressionChapter(chapterID):
            return False
        return True if chapterID and self.__battlePass.isBought(chapterID=chapterID) else self.__battlePass.isAllMainChaptersBought()

    @property
    def isCompleted(self):
        chapterIDs = self.__battlePass.getMainChapterIDs()
        return all((self.__battlePass.isChapterCompleted(chapter) for chapter in chapterIDs))

    @property
    def isPostProgressionActive(self):
        return self.__battlePass.isPostProgressionActive()

    @property
    def isAnyExtraActive(self):
        return self.__battlePass.getCurrentChapterID() in self.__battlePass.getExtraChapterIDs()

    @property
    def isAllExtraCompleted(self):
        return all((self.__battlePass.isChapterCompleted(chapterID) for chapterID in self.__battlePass.getExtraChapterIDs()))

    @property
    def isPaused(self):
        return self.__battlePass.isPaused() or not self.__battlePass.isGameModeEnabled(self._getCurrentArenaBonusType())

    @property
    def hasExtra(self):
        return self.__battlePass.hasExtra()

    @property
    def isHoliday(self):
        return self.__battlePass.isHoliday()

    @property
    def battlePassState(self):
        return self.__battlePass.getState()

    @property
    def progress(self):
        points, limit = self.__battlePass.getLevelProgression(self.chapterID)
        return FULL_PROGRESS // (limit or FULL_PROGRESS) * points

    @property
    def freePoints(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.BIT.value, 0)

    def onPrbEntitySwitched(self):
        self._updateData()

    def _start(self):
        self._addListeners()
        self._updateData()

    def _stop(self):
        self._removeListeners()

    def _updateData(self, *_):
        pass

    def _onChapterChanged(self, *_):
        self._updateData()

    def _onPointsUpdated(self, *_):
        self._updateData()

    def _onOffersUpdated(self, *_):
        self._updateData()

    def _onClick(self):
        showBattlePass()

    def _getListeners(self):
        return ((events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.__battlePass.onPointsUpdated, self._onPointsUpdated),
         (self.__battlePass.onBattlePassIsBought, self._updateData),
         (self.__battlePass.onSeasonStateChanged, self._updateData),
         (self.__battlePass.onExtraChapterExpired, self._updateData),
         (self.__battlePass.onBattlePassSettingsChange, self._updateData),
         (self.__battlePass.onChapterChanged, self._onChapterChanged),
         (self.__battlePass.onOffersUpdated, self._onOffersUpdated))

    def _addListeners(self):
        self.startGlobalListening()

    def _removeListeners(self):
        self.stopGlobalListening()

    def _getTooltip(self):
        if self.isPaused:
            return R.invalid()
        if self.isCompleted and self.isHoliday:
            return R.views.mono.battle_pass.tooltips.completed()
        return R.views.mono.battle_pass.tooltips.no_chapter() if not self.chapterID and not self.isHoliday else R.views.mono.battle_pass.tooltips.in_progress()

    def _getNotChosenRewardCount(self):
        return self.__battlePass.getNotChosenRewardCount()

    def _getCurrentArenaBonusType(self):
        return getSupportedCurrentArenaBonusType(self._getQueueType())

    def _getQueueType(self):
        dispatcher = g_prbLoader.getDispatcher()
        return None if dispatcher is None else dispatcher.getEntity().getQueueType()

    def __onAwardViewClose(self, _):
        self._updateData()
