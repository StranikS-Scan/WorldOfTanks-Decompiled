# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints_ctrl.py
from collections import namedtuple
import logging
import time
from typing import List, Tuple
import BigWorld
import constants
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from gui.shared import battle_hints
from gui.shared.battle_hints import BattleHintData
from shared_utils import findFirst
import SoundGroups
_logger = logging.getLogger(__name__)
HintRequest = namedtuple('HintRequest', ('hint', 'data', 'requestTime'))

class BattleHintComponent(object):
    HINT_MIN_SHOW_TIME = 2.0

    def __init__(self):
        super(BattleHintComponent, self).__init__()
        self.currentHint = None
        self.currentHintStartTime = 0
        return

    def showHint(self, hint, data):
        _logger.debug('Show battle hint hintName=%s, priority=%d', hint.name, hint.priority)
        self.__playHintSound(hint, data)
        vo = self._makeVO(hint, data)
        self._showHint(vo)
        self.currentHintStartTime = time.time()
        self.currentHint = hint

    def hideHint(self, hint=None):
        if hint is None or self.currentHint == hint:
            self._hideHint()
            self.currentHint = None
        else:
            _logger.warning('Failed to hide hint name=%s', hint.name)
        return

    def _showHint(self, hintData):
        raise NotImplementedError

    def _hideHint(self):
        raise NotImplementedError

    def _getSoundNotification(self, hint, data):
        return hint.soundNotification

    def _makeVO(self, hint, data):
        return hint.makeVO(data)

    def __playHintSound(self, hint, data):
        if hint.soundFx is not None:
            SoundGroups.g_instance.playSound2D(hint.soundFx)
        sound = self._getSoundNotification(hint, data)
        if sound is not None:
            player = BigWorld.player()
            soundNotifications = getattr(player, 'soundNotifications', None)
            if soundNotifications:
                soundNotifications.play(sound)
        return


class BattleHintsController(ViewComponentsController):
    _DEFAULT_HINT_NAME = 'default'

    def __init__(self, hintsData):
        super(BattleHintsController, self).__init__()
        self.__hintsData = {hint.name:hint for hint in hintsData}
        self.__currentComponent = None
        self.__delayedHints = []
        self.__currentHintCallback = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.__cancelCurrentHintCallback()

    def showHint(self, hintName, data=None):
        component, hint = self.__getComponentAndHint(hintName)
        if hint and component:
            _logger.debug('Request battle hint hintName=%s, priority=%d', hint.name, hint.priority)
            if self.__currentComponent:
                self.__resolveHintsConflict(hint, data)
            else:
                self.__showHint(hint, data, component)
        else:
            _logger.error('Failed to show hint name=%s', hintName)

    def __showHint(self, hint, data, component):
        component.showHint(hint, data)
        self.__currentComponent = component
        if hint.duration is not None:
            self.__currentHintCallback = BigWorld.callback(hint.duration, self.__hideHintCallback)
        return

    def __resolveHintsConflict(self, hint, data):
        requestTime = time.time()
        self.__delayedHints.append(HintRequest(hint, data, requestTime))
        if hint.priority > self.__currentComponent.currentHint.priority:
            showTimeLeft = self.__currentComponent.HINT_MIN_SHOW_TIME - (requestTime - self.__currentComponent.currentHintStartTime)
            if showTimeLeft <= 0:
                self.__updateCurrentHint()
            else:
                self.__cancelCurrentHintCallback()
                self.__currentHintCallback = BigWorld.callback(showTimeLeft, self.__hideHintCallback)

    def __cancelCurrentHintCallback(self):
        if self.__currentHintCallback is not None:
            BigWorld.cancelCallback(self.__currentHintCallback)
            self.__currentHintCallback = None
        return

    def __hideHintCallback(self):
        self.__currentHintCallback = None
        self.hideHint(self.__currentComponent.currentHint.name)
        return

    def __updateCurrentHint(self):
        self.__cancelCurrentHintCallback()
        self.hideHint(self.__currentComponent.currentHint.name)

    def hideHint(self, hintName):
        component, hint = self.__getComponentAndHint(hintName)
        if hint and component:
            component.hideHint(hint)
            if component == self.__currentComponent:
                self.__cancelCurrentHintCallback()
                self.__currentComponent = None
            self.__showDelayedHint()
        else:
            _logger.error('Failed to hide hint name=%s', hintName)
        return

    def __getHint(self, hintName):
        hint = self.__hintsData.get(hintName)
        if hint is None and constants.IS_DEVELOPMENT:
            _logger.warning('Failed to find hint name=%s. Default name used instead', hintName)
            hint = self.__hintsData.get(self._DEFAULT_HINT_NAME)
            hint = hint._replace(rawMessage=hintName)
        return hint

    def __getComponentAndHint(self, hintName):
        component = None
        hint = self.__getHint(hintName)
        if hint:
            alias = hint.componentAlias
            component = findFirst(lambda comp: comp.getAlias() == alias, self._viewComponents)
            if not component:
                _logger.error('Unknown component alias=%s', alias)
        else:
            _logger.error('Unknown hint name=%s', hintName)
        return (component, hint)

    def __showDelayedHint(self):
        currentTime = time.time()
        self.__delayedHints = [ r for r in self.__delayedHints if currentTime - r.requestTime < r.hint.maxWaitTime ]
        if self.__delayedHints:
            maxPriorityHint = max(self.__delayedHints, key=lambda request: request.hint.priority)
            self.__delayedHints.remove(maxPriorityHint)
            hint, data, _ = maxPriorityHint
            self.showHint(hint.name, data)


def createBattleHintsController():
    return BattleHintsController(battle_hints.makeHintsData())
