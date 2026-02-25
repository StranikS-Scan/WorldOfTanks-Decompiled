# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/battle/cosmic_hud/progress_bar_manager.py
import BigWorld
import functools
import logging
import typing
from helpers import time_utils
from shared_utils import safeCancelCallback
from cosmic_event_common.cosmic_constants import LOOT_ITEM_ID, LOOT_STATE
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.cosmic_progress_bar import CosmicProgressBar, ProgressBarType
from cosmic_sound import CosmicBattleSounds
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from collections import Callable
    from typing import Dict
_logger = logging.getLogger(__name__)

class CosmicProgressBarsManager(object):

    def __init__(self, progressBars):
        self._progressBars = progressBars
        self.__setupHandlers = self.__initSetupHandlers()
        self.__updateHandlers = self.__initUpdateHandlers()
        self.__barTimers = {}
        self.__progressBarIdToArrayID = {}
        for loot in BigWorld.entities.valuesOfType('CosmicLoot'):
            if loot.itemID == LOOT_ITEM_ID.COSMIC_CORAL and loot.state == LOOT_STATE.SPAWNED:
                ctx = {'totalTime': loot.lifeTime,
                 'timeLeft': loot.lifeTimeRemained}
                self.createProgressBar(ProgressBarType.CORAL, loot.id, ctx)

    def stop(self):
        for barID in self.__progressBarIdToArrayID.keys():
            self.destroyProgressBar(barID)

        self.__progressBarIdToArrayID.clear()
        self.__progressBarIdToArrayID = None
        self.__setupHandlers = None
        self.__updateHandlers = None
        return

    def createProgressBar(self, barType, barID, ctx):
        if barID in self.__progressBarIdToArrayID:
            _logger.info('ProgressBar with id = %s already exists. Updating info instead', barID)
            self.updateProgressBar(barID, ctx)
            return
        else:
            progressBarModel = CosmicProgressBar()
            progressBarModel.setBarType(barType)
            if barType not in self.__setupHandlers:
                _logger.error('There is no setup handler for given barType. barID = %s, barType = %s', barID, barType)
                return
            totalTime = ctx.get('totalTime', 0)
            timeLeft = ctx.get('timeLeft', 0)
            if totalTime is not None:
                progressBarModel.setTotalTime(totalTime)
            if timeLeft is not None:
                progressBarModel.setTimeLeft(timeLeft)
            if timeLeft or totalTime:
                self.__setProgressBarTimer(barID, progressBarModel, timeLeft)
            self.__setupHandlers[barType](progressBarModel, ctx)
            self._progressBars.addViewModel(progressBarModel)
            arrID = len(self._progressBars) - 1
            self.__progressBarIdToArrayID[barID] = arrID
            return

    def destroyProgressBar(self, barID):
        arrID = self.__progressBarIdToArrayID.get(barID, -1)
        if arrID == -1:
            return
        else:
            timerID = self.__barTimers.pop(barID, None)
            if timerID is not None:
                safeCancelCallback(timerID)
            self._progressBars.remove(arrID)
            self.__progressBarIdToArrayID.pop(barID)
            for keyID, arrayID in self.__progressBarIdToArrayID.iteritems():
                if arrayID > arrID:
                    self.__progressBarIdToArrayID[keyID] = arrayID - 1

            return

    def updateProgressBar(self, barID, ctx):
        arrID = self.__progressBarIdToArrayID.get(barID, -1)
        if arrID == -1:
            _logger.error('ProgressBar with id %s not found!', barID)
            return
        else:
            progressBarModel = self._progressBars.getValue(arrID)
            barType = progressBarModel.getBarType()
            if barType not in self.__setupHandlers:
                _logger.error('There is no setup handler for given barType. barID = %s, barType = %s', barID, barType)
                return
            totalTime = ctx.get('totalTime')
            timeLeft = ctx.get('timeLeft')
            if totalTime is not None:
                progressBarModel.setTotalTime(totalTime)
            if timeLeft is not None:
                progressBarModel.setTimeLeft(timeLeft)
            if timeLeft or totalTime:
                self.__setProgressBarTimer(barID, progressBarModel, timeLeft)
            self.__updateHandlers[barType](progressBarModel, ctx)
            return

    def __updateCoralProgressBar(self, progressBarModel, ctx):
        if progressBarModel.getBarType() != ProgressBarType.CORAL:
            _logger.error('Trying to update coral context on non-coral progressBar')
            return

    def __updateArtifactProgressBar(self, progressBarModel, ctx):
        if progressBarModel.getBarType() != ProgressBarType.ARTIFACT_ZONE:
            _logger.error('Trying to update artifact_zone context on non-artifact zone progressBar')
            return
        else:
            if ctx.get('activePlayersCount', None) is not None:
                progressBarModel.setActivePlayers(ctx.get('activePlayersCount'))
            return

    def __setupCoralProgressBar(self, progressBarModel, ctx):
        if progressBarModel.getBarType() != ProgressBarType.CORAL:
            _logger.error('Trying to apply coral context to non-coral progressBar')
            return

    def __setupArtifactProgressBar(self, progressBarModel, ctx):
        if progressBarModel.getBarType() != ProgressBarType.ARTIFACT_ZONE:
            _logger.error('Trying to apply artifact_zone context to non-artifact zone progressBar')
            return
        progressBarModel.setActivePlayers(ctx.get('activePlayersCount', 0))

    def __initSetupHandlers(self):
        return {ProgressBarType.CORAL: self.__setupCoralProgressBar,
         ProgressBarType.ARTIFACT_ZONE: self.__setupArtifactProgressBar}

    def __initUpdateHandlers(self):
        return {ProgressBarType.CORAL: self.__updateCoralProgressBar,
         ProgressBarType.ARTIFACT_ZONE: self.__updateArtifactProgressBar}

    def __setProgressBarTimer(self, barID, progressBarModel, timeLeft):
        timerID = self.__barTimers.pop(barID, None)
        if timerID is not None:
            _logger.info('Timer for barID %s already exists! Replacing by new one', barID)
            safeCancelCallback(timerID)
        progressBarModel.setTimeLeft(timeLeft)
        timerID = BigWorld.callback(time_utils.ONE_SECOND, functools.partial(self.__onTimerTick, barID, progressBarModel, timeLeft))
        self.__barTimers[barID] = timerID
        return

    def __onTimerTick(self, barID, progressBarModel, timeLeft):
        timerID = self.__barTimers.pop(barID, None)
        if timerID is None:
            _logger.error('Timer for barID %s not found! but onTimerTick has called', barID)
            return
        else:
            if progressBarModel.getBarType() == ProgressBarType.CORAL:
                CosmicBattleSounds.setTimerSound(timeLeft)
            timeLeft -= 1
            if timeLeft <= 0:
                return
            progressBarModel.setTimeLeft(timeLeft)
            timerID = BigWorld.callback(time_utils.ONE_SECOND, functools.partial(self.__onTimerTick, barID, progressBarModel, timeLeft))
            self.__barTimers[barID] = timerID
            return
