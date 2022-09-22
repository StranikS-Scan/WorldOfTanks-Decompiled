# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints_ctrl.py
import time
import logging
from collections import namedtuple
import BigWorld
import SoundGroups
import constants
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import battle_hints
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
HintRequest = namedtuple('HintRequest', ('hint', 'data', 'requestTime'))

class IBattleHintView(object):

    def showHint(self, hint, data):
        pass

    def hideHint(self, hint=None):
        pass


class BattleHintComponent(IBattleHintView):
    _HINT_MIN_SHOW_TIME = 2.0

    def __init__(self):
        super(BattleHintComponent, self).__init__()
        self.__currentHint = None
        self.__hintStartTime = 0
        self.__hintRequests = []
        self.__hideCallback = None
        return

    def showHint(self, hint, data):
        currentHint = self.__currentHint
        if currentHint:
            requestTime = time.time()
            self.__hintRequests.append(HintRequest(hint, data, requestTime))
            if hint.priority > currentHint.priority:
                showTimeLeft = self._HINT_MIN_SHOW_TIME - (time.time() - self.__hintStartTime)
                if showTimeLeft <= 0:
                    self.__hideCurrentHint()
                else:
                    self.__hideHintCallback()
                    self.__hideCallback = BigWorld.callback(showTimeLeft, self.__hideCurrentHint)
        else:
            self.__showHint(hint, data)

    def hideHint(self, hint=None):
        if hint is None or self.__currentHint == hint:
            self.__hideCurrentHint()
        else:
            _logger.warning('Failed to hide hint name=%s', hint.name)
        return

    def _showHint(self, hintData):
        raise NotImplementedError

    def _hideHint(self):
        raise NotImplementedError

    def _getSoundNotification(self, hint, data):
        return hint.soundNotification

    def __showHint(self, hint, data):
        if hint.soundFx is not None:
            SoundGroups.g_instance.playSound2D(hint.soundFx)
        sound = self._getSoundNotification(hint, data)
        if sound is not None:
            player = BigWorld.player()
            if hasattr(player, 'soundNotifications'):
                soundNotifications = player.soundNotifications
                if soundNotifications is not None:
                    soundNotifications.play(sound)
        _logger.debug('Show battle hint hintName=%s, priority=%d', hint.name, hint.priority)
        self._showHint(hint.makeVO(data))
        self.__currentHint = hint
        self.__hintStartTime = time.time()
        duration = hint.duration
        if duration is not None:
            self.__hideHintCallback()
            self.__hideCallback = BigWorld.callback(duration, self.__hideCurrentHint)
        return

    def __hideCurrentHint(self):
        self.__hideHintCallback()
        self._hideHint()
        self.__currentHint = None
        self.__showDelayedHint()
        return

    def __hideHintCallback(self):
        if self.__hideCallback is not None:
            BigWorld.cancelCallback(self.__hideCallback)
            self.__hideCallback = None
        return

    def __showDelayedHint(self):
        currentTime = time.time()
        self.__hintRequests = [ r for r in self.__hintRequests if currentTime - r.requestTime < r.hint.maxWaitTime ]
        delayedHints = self.__hintRequests
        if not delayedHints:
            return
        maxPriorityHint = max(delayedHints, key=lambda r: r.hint.priority)
        delayedHints.remove(maxPriorityHint)
        hint, data, _ = maxPriorityHint
        self.__showHint(hint, data)


class BattleHintsController(ViewComponentsController):
    _DEFAULT_HINT_NAME = 'default'

    def __init__(self, hintsData):
        super(BattleHintsController, self).__init__()
        self.__hintsData = {hint.name:hint for hint in hintsData}

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def showHint(self, hintName, data=None):
        hint = self.__getHint(hintName)
        if hint:
            for view in self.__iterComponentsByAlias(hint.componentAlias):
                view.showHint(hint, data)

    def hideHint(self, hintName):
        hint = self.__getHint(hintName)
        if hint:
            for view in self.__iterComponentsByAlias(hint.componentAlias):
                view.hideHint(hint)

    def __getHint(self, hintName):
        hint = self.__hintsData.get(hintName)
        if hint is None and constants.IS_DEVELOPMENT:
            hint = self.__hintsData.get(self._DEFAULT_HINT_NAME)
            hint = hint._replace(rawMessage=hintName)
        if not hint:
            _logger.warning('Unknown hint name=%s', hintName)
        return hint

    def __iterComponentsByAlias(self, componentAliases):
        for alias in componentAliases:
            component = findFirst(lambda comp, cAlias=alias: comp.getAlias() == cAlias, self._viewComponents)
            if component:
                yield component
            _logger.error('Unknown component alias=%s', alias)


def createBattleHintsController():
    return BattleHintsController(battle_hints.makeHintsData())
