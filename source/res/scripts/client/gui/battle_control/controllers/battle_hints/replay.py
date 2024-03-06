# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints/replay.py
import typing
from typing import Optional, Dict, Union
import BattleReplay
from BattleReplay import CallbackDataNames
from PlayerEvents import g_playerEvents
from gui.battle_control.controllers.battle_hints.common import getLogger
from hints.battle import manager as battleHintsModelsMgr
if typing.TYPE_CHECKING:
    from hints.battle.schemas.base import CHMType
    from gui.battle_control.controllers.battle_hints.queues import BattleHint
    from gui.battle_control.controllers.battle_hints.controller import BattleHintsController
_logger = getLogger('Replay')

def getReplayController(battleHintsCtrl):
    if BattleReplay.isRecording():
        return BattleHintsReplayRecorder()
    elif BattleReplay.isPlaying():
        return BattleHintsReplayPlayer(battleHintsCtrl)
    else:
        _logger.debug('Could not get a replay controller.')
        return None


class BattleHintsReplayRecorder(object):

    def __init__(self):
        g_playerEvents.onShowBattleHint += self.onShowBattleHint
        g_playerEvents.onHideBattleHint += self.onHideBattleHint

    def fini(self):
        g_playerEvents.onShowBattleHint -= self.onShowBattleHint
        g_playerEvents.onHideBattleHint -= self.onHideBattleHint

    def onShowBattleHint(self, battleHint):
        self.serializeMethod(CallbackDataNames.SHOW_BATTLE_HINT, battleHint.uniqueName, battleHint.params)

    def onHideBattleHint(self, battleHint):
        self.serializeMethod(CallbackDataNames.HIDE_BATTLE_HINT, battleHint.uniqueName, battleHint.params)

    def serializeMethod(self, eventName, hintName, params):
        if BattleReplay.isRecording():
            BattleReplay.g_replayCtrl.serializeCallbackData(eventName, (hintName, params))


class BattleHintsReplayPlayer(object):

    def __init__(self, battleHintsCtrl):
        self._modelsMgr = battleHintsModelsMgr.get()
        self.battleHintsCtrl = battleHintsCtrl
        self.__currentHint = None
        BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.SHOW_BATTLE_HINT, self._showHint)
        BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.HIDE_BATTLE_HINT, self._hideHint)
        return

    def fini(self):
        if self.__currentHint:
            self.__currentHint.cancelFadeOut()
            self.__currentHint = None
        self.battleHintsCtrl = None
        BattleReplay.g_replayCtrl.delDataCallback(CallbackDataNames.SHOW_BATTLE_HINT, self._showHint)
        BattleReplay.g_replayCtrl.delDataCallback(CallbackDataNames.HIDE_BATTLE_HINT, self._hideHint)
        return

    def _getHint(self, hintName, params):
        if not self._modelsMgr:
            return None
        else:
            model = self._modelsMgr.get(hintName)
            if not model:
                return None
            alias = model.props.component
            component = self.battleHintsCtrl.getComponent(alias)
            if not component:
                return None
            queueParams = component.getBattleHintsQueueParams()
            return queueParams.createHint(model, component, params=params)

    def _showHint(self, hintName, params):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            hint = self._getHint(hintName, params)
            if hint is not None:
                hint.show()
                self.__currentHint = hint
            return

    def _hideHint(self, hintName, params):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            hint = self._getHint(hintName, params)
            if hint is not None:
                hint.hide()
                self.__currentHint = None
            return
