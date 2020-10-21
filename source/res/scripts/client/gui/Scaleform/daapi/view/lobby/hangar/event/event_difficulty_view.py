# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_difficulty_view.py
import GUI
from adisp import process
from constants import REQUEST_COOLDOWN
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getDifficultyStars
from gui.prb_control.entities.event.squad.entity import EventBattleSquadEntity
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from gui.server_events.game_event.event_processors import ChangeSelectedDifficultyLevel
from skeletons.gui.game_event_controller import IGameEventController
from gui.Scaleform.daapi.view.meta.EventDifficultyViewMeta import EventDifficultyViewMeta
from gui.server_events.events_dispatcher import showEventHangar
from gui.impl.gen import R
from gui.impl import backport
PROGRESS_BAR_MAX_VALUE = 100

class EventDifficultyView(EventDifficultyViewMeta, IGlobalListener):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, *args, **kwargs):
        super(EventDifficultyView, self).__init__(*args, **kwargs)
        self.__blur = GUI.WGUIBackgroundBlur()

    def closeView(self):
        showEventHangar()

    def _populate(self):
        super(EventDifficultyView, self)._populate()
        self._callbackDelayer = CallbackDelayer()
        self.startGlobalListening()
        self._updateDifficultyLevels()
        self.gameEventController.getDifficultyController().onItemsUpdated += self._updateDifficultyLevels
        self.gameEventController.onSelectedDifficultyLevelChanged += self._updateDifficultyLevels
        self.__blur.enable = True

    def _dispose(self):
        self.__blur.enable = False
        self._callbackDelayer.destroy()
        self.stopGlobalListening()
        self.gameEventController.getDifficultyController().onItemsUpdated -= self._updateDifficultyLevels
        self.gameEventController.onSelectedDifficultyLevelChanged -= self._updateDifficultyLevels
        self._showWaiting(False)
        super(EventDifficultyView, self)._dispose()

    def onUnitPlayerBecomeCreator(self, pInfo):
        if not pInfo.isCurrentPlayer():
            self.closeView()

    def _showWaiting(self, show):
        if show:
            Waiting.show('sinhronize')
        else:
            Waiting.hide('sinhronize')

    @process
    def selectDifficulty(self, idx):
        result = self.gameEventController.setSelectedDifficultyLevel(idx)
        if result:
            if self.gameEventController.isEnabled() and isinstance(self.prbEntity, EventBattleSquadEntity) and self.prbEntity.isCommander():
                self._showWaiting(True)
                yield ChangeSelectedDifficultyLevel(idx).request()
                self._callbackDelayer.delayCallback(REQUEST_COOLDOWN.CMD_CHANGE_SELECTED_DIFFICULTY_LEVEL, lambda : self._showWaiting(False))
            self._updateDifficultyLevels()

    def _updateDifficultyLevels(self):
        levelsData = {'levels': [ self.getItemVO(level) for level in self.gameEventController.getDifficultyLevels() ]}
        self.as_setDataS(levelsData)
        difficultyController = self.gameEventController.getDifficultyController()
        progressConditionText = R.strings.event.event.difficulty.unlock_condition()
        currentDifficultyLevel = difficultyController.getCurrentProgressItem().getDifficultyLevel()
        progressValue = PROGRESS_BAR_MAX_VALUE
        conditionText = ''
        progressItem = difficultyController.getNextProgressItem()
        if progressItem:
            needToUnlock = difficultyController.getProgressLeftToNextLevel()
            progressData = [ (item.getCurrentProgress(), item.getMaxProgress()) for item in difficultyController.getItems() if item.getMaxProgress() != 0 ]
            maxItemProgress = PROGRESS_BAR_MAX_VALUE / len(progressData)
            progressValue = sum((int(maxItemProgress * progress[0] / float(progress[1])) for progress in progressData))
            conditionText = backport.text(progressConditionText, winCount=needToUnlock, difficultyStars=getDifficultyStars(currentDifficultyLevel, isMedium=True))
        self.as_setProgressS(progressValue, conditionText, currentDifficultyLevel)

    def getItemVO(self, level):
        title = R.strings.event.event.difficulty.level.num(level).title()
        description = R.strings.event.event.difficulty.level.num(level).reward_desc()
        numPhases = R.strings.event.event.difficulty.level.num(level).num_phases()
        isSelectedLevel = self.gameEventController.getSelectedDifficultyLevel() == level
        itemProgress = self.gameEventController.getDifficultyController().getItemOnDifficultyLevel(level)
        return {'numPhases': backport.text(numPhases),
         'title': backport.text(title),
         'description': backport.text(description),
         'level': level,
         'selected': isSelectedLevel,
         'enabled': itemProgress.isCompleted()}
