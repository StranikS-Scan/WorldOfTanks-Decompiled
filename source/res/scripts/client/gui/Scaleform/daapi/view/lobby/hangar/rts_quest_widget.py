# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/rts_quest_widget.py
import logging
from helpers import dependency
from constants import QUEUE_TYPE
from daily_quest_widget import DailyQuestWidget
from gui.impl.lobby.rts.quests_widget_view import RtsQuestsWidgetView
from skeletons.gui.game_control import IRTSProgressionController
from skeletons.gui.game_control import IRTSBattlesController
_logger = logging.getLogger(__name__)

class RtsQuestWidget(DailyQuestWidget):
    __progressionCtrl = dependency.descriptor(IRTSProgressionController)
    __battlesController = dependency.instance(IRTSBattlesController)

    def onPrbEntitySwitched(self):
        if not self._isRTSSelected():
            self._animateHide()
        else:
            self._showOrHide()

    def _populate(self):
        super(RtsQuestWidget, self)._populate()
        self.__battlesController.onControlModeChanged += self.__onGameModeChanged

    def _dispose(self):
        self.__battlesController.onControlModeChanged -= self.__onGameModeChanged
        super(RtsQuestWidget, self)._dispose()

    def _makeInjectView(self):
        return RtsQuestsWidgetView()

    def _shouldHide(self):
        return not self.__progressionCtrl.isEnabled() or self.promoController.isTeaserOpen() or not self._isRTSSelected()

    def _isRTSSelected(self):
        queueType = self.__getQueueType()
        return queueType == QUEUE_TYPE.RTS or queueType == QUEUE_TYPE.RTS_1x1

    def _getQuests(self):
        isCommander = self.__battlesController.isCommander()
        return self.__progressionCtrl.getQuests(isCommander, includeFuture=False)

    def _executeShowOrHide(self):
        haveQuestsToShow = self._hasIncompleteQuests() or self._hasQuestStatusChanged()
        if self._shouldHide() or not haveQuestsToShow:
            self._hide()
            return
        if haveQuestsToShow:
            self._show()

    def __getQueueType(self):
        return self.prbEntity.getQueueType() if self.prbEntity else QUEUE_TYPE.UNKNOWN

    def __onGameModeChanged(self, *_):
        self._showOrHide()
