# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_difficulty_unlock_view.py
import GUI
from adisp import process
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.DifficultyUnlockMeta import DifficultyUnlockMeta
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.event.squad.entity import EventBattleSquadEntity
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
PROGRESS_BAR_MAX_VALUE = 100

class EventDifficultyUnlockView(DifficultyUnlockMeta, IGlobalListener):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, *args, **kwargs):
        super(EventDifficultyUnlockView, self).__init__(*args, **kwargs)
        self.__blur = GUI.WGUIBackgroundBlur()

    def _populate(self):
        super(EventDifficultyUnlockView, self)._populate()
        self.as_setDifficultyS(self.gameEventController.getMaxUnlockedDifficultyLevel(), self._enableDifficultyBtn())
        self.as_blurOtherWindowsS(WindowLayer.VIEW)
        self.__blur.enable = True

    def _dispose(self):
        self.__blur.enable = False
        super(EventDifficultyUnlockView, self)._dispose()

    def _enableDifficultyBtn(self):
        if not isinstance(self.prbEntity, EventBattleSquadEntity):
            return True
        _, unit = self.prbEntity.getUnit()
        pInfo = self.prbEntity.getPlayerInfo()
        if not unit or not pInfo:
            return True
        return False if unit.isPrebattlesSquad() and unit.getCommanderDBID() != pInfo.dbID else True

    def _setDifficultyLevelShown(self):
        level = self.gameEventController.getMaxUnlockedDifficultyLevel()
        difficultyCtrl = self.gameEventController.getDifficultyController()
        difficultyCtrl.setDifficultyLevelShown(level)

    def onCloseClick(self):
        self._setDifficultyLevelShown()
        self.destroy()

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @process
    def __doSelectAction(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))

    def onDifficultyChangeClick(self):
        self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)
        from gui.server_events.events_dispatcher import showEventTab
        showEventTab(VIEW_ALIAS.EVENT_DIFFICULTY)
        self._setDifficultyLevelShown()
        self.destroy()
