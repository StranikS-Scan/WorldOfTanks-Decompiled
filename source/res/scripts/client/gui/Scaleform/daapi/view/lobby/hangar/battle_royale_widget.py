# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/battle_royale_widget.py
import logging
import typing
import SoundGroups
from gui.Scaleform.daapi.view.meta.BattleRoyaleHangarWidgetMeta import BattleRoyaleHangarWidgetMeta
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.battle_royale.royale_builders.widget_vos import StateBlock, WidgetPreferences, getVOsSequence
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
if typing.TYPE_CHECKING:
    from gui.battle_royale.royale_models import Title
_logger = logging.getLogger(__name__)

class BattleRoyaleResultsWidget(BattleRoyaleHangarWidgetMeta):
    _royaleController = dependency.descriptor(IBattleRoyaleController)

    def update(self, lastTitleID=None, lastMaxTitleID=None, currentTitleID=None, titlesChain=None):
        lastTitleID = self._royaleController.getClientTitle().title if lastTitleID is None else lastTitleID
        lastMaxTitleID = self._royaleController.getClientMaxTitle().title if lastMaxTitleID is None else lastMaxTitleID
        currentTitleID = self._royaleController.getCurrentTitle().title if currentTitleID is None else currentTitleID
        titlesChain = self._royaleController.getCachedTitlesChain(min(lastTitleID, currentTitleID), max(lastTitleID, currentTitleID) + 1) if titlesChain is None else titlesChain
        preferences = WidgetPreferences(self._royaleController.getMinPossibleTitle(), self._royaleController.getMaxPossibleTitle(), self._isHuge())
        statesSequence = self.__buildStatesSequence(preferences, lastTitleID, currentTitleID, lastMaxTitleID, titlesChain)
        vosSequence = getVOsSequence(preferences, statesSequence, titlesChain)
        self._royaleController.updateClientValues()
        if vosSequence:
            self.as_setDataS(vosSequence)
        return

    def onSoundTrigger(self, triggerName):
        SoundGroups.g_instance.playSound2D(triggerName)

    def onWidgetClick(self):
        pass

    @classmethod
    def _isHuge(cls):
        return True

    @staticmethod
    def __buildStatesSequence(preferences, lastTitleID, currentTitleID, maxTitleID, titles):
        states = []
        lastTitle = titles[lastTitleID]
        currentTitle = titles[currentTitleID]
        minPossibleTitleID = preferences.minPossibleTitleID
        maxPossibleTitleID = preferences.maxPossibleTitleID
        if maxTitleID < lastTitleID:
            _logger.error('Last title can not be more then max title')
        if currentTitle.isNewForPlayer():
            if lastTitle.isAcquired():
                for titleID, nextTitleID in zip(range(lastTitleID, currentTitleID), range(lastTitleID + 1, currentTitleID + 1)):
                    if titleID == minPossibleTitleID:
                        if titleID < maxTitleID:
                            states.append(StateBlock(BATTLEROYALE_ALIASES.FIRST_TITLE_REACHIVE_STATE, titleID, nextTitleID))
                        else:
                            states.append(StateBlock(BATTLEROYALE_ALIASES.FIRST_TITLE_RECEIVE_STATE, titleID, nextTitleID))
                    if nextTitleID == maxPossibleTitleID:
                        if titleID < maxTitleID:
                            states.append(StateBlock(BATTLEROYALE_ALIASES.LAST_TITLE_REACHIVE_STATE, titleID, nextTitleID))
                        else:
                            states.append(StateBlock(BATTLEROYALE_ALIASES.LAST_TITLE_RECEIVE_STATE, titleID, nextTitleID))
                    if titleID < maxTitleID:
                        states.append(StateBlock(BATTLEROYALE_ALIASES.TITLE_REACHIVE_STATE, titleID, nextTitleID))
                    states.append(StateBlock(BATTLEROYALE_ALIASES.TITLE_RECEIVE_STATE, titleID, nextTitleID))

            if lastTitle.isLost():
                for titleID, prevTitleID in zip(reversed(range(currentTitleID + 1, lastTitleID + 1)), reversed(range(currentTitleID, lastTitleID))):
                    if prevTitleID == minPossibleTitleID:
                        states.append(StateBlock(BATTLEROYALE_ALIASES.FIRST_TITLE_LOST_STATE, titleID, prevTitleID))
                    if titleID == maxPossibleTitleID:
                        states.append(StateBlock(BATTLEROYALE_ALIASES.LAST_TITLE_LOST_STATE, titleID, prevTitleID))
                    states.append(StateBlock(BATTLEROYALE_ALIASES.TITLE_LOST_STATE, titleID, prevTitleID))

            return states
        state = BATTLEROYALE_ALIASES.TITLE_IDLE_STATE
        if currentTitleID == minPossibleTitleID:
            state = BATTLEROYALE_ALIASES.TITLE_INIT_STATE
        if currentTitleID == maxPossibleTitleID:
            state = BATTLEROYALE_ALIASES.TITLE_FINI_STATE
        states = [StateBlock(state, currentTitleID, currentTitleID)]
        return states


class BattleRoyaleHangarWidget(BattleRoyaleResultsWidget):

    def onWidgetClick(self):
        self._royaleController.showBattleRoyalePage(ctx={'selectedItemID': BATTLEROYALE_CONSTS.BATTLE_ROYALE_PROGRESS_ID})

    @classmethod
    def _isHuge(cls):
        return False
