# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints_ctrl.py
import time
import logging
from collections import namedtuple
from functools import partial
import BigWorld
import SoundGroups
import constants
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import battle_hints
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
HintRequest = namedtuple('HintRequest', ('component', 'hint', 'data', 'requestTime'))

class BattleHintComponent(object):

    def showHint(self, hint, data):
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
        vo = self._makeVO(hint, data)
        self._showHint(vo)
        return

    def hideHint(self):
        self._hideHint()

    def _showHint(self, hintData):
        raise NotImplementedError

    def _hideHint(self):
        raise NotImplementedError

    def _getSoundNotification(self, hint, data):
        return hint.soundNotification

    def _makeVO(self, hint, data):
        return hint.makeVO(data)


class BattleHintsController(ViewComponentsController):
    _HINT_MIN_SHOW_TIME = 2.0
    _DEFAULT_HINT_NAME = 'default'

    def __init__(self, hintsData):
        super(BattleHintsController, self).__init__()
        self.__hintsData = {hint.name:hint for hint in hintsData}
        self.__currentHint = None
        self.__hintStartTime = 0
        self.__hintRequests = []
        self.__hideCallback = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.__hideHintCallback()

    def showHint(self, hintName, data=None):
        component, hint = self.__getComponentAndHint(hintName)
        if hint is None or component is None:
            _logger.error('Failed to show hint name=%s', hintName)
            return
        else:
            _logger.debug('Request battle hint hintName=%s, priority=%d', hint.name, hint.priority)
            currentHint = self.__currentHint
            if currentHint:
                requestTime = time.time()
                self.__hintRequests.append(HintRequest(component, hint, data, requestTime))
                if hint.priority > currentHint.priority:
                    showTimeLeft = self._HINT_MIN_SHOW_TIME - (time.time() - self.__hintStartTime)
                    if showTimeLeft <= 0:
                        self.__hideCurrentHint(component)
                    else:
                        self.__hideHintCallback()
                        self.__hideCallback = BigWorld.callback(showTimeLeft, partial(self.__hideCurrentHint, component))
            else:
                self.__showHint(component, hint, data)
            return

    def hideHint(self, hintName):
        component, hint = self.__getComponentAndHint(hintName)
        if hint is None or self.__currentHint != hint:
            _logger.warning('Failed to hide hint name=%s', hintName)
            return
        else:
            if component:
                component.hideHint()
            else:
                _logger.error('Failed to hide hint name=%s', hintName)
            return

    def __getComponentAndHint(self, hintName):
        component = None
        hint = self.__hintsData.get(hintName)
        if hint is None and constants.IS_DEVELOPMENT:
            hint = self.__hintsData.get(self._DEFAULT_HINT_NAME)
            hint = hint._replace(rawMessage=hintName)
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
        self.__hintRequests = [ r for r in self.__hintRequests if currentTime - r.requestTime < r.hint.maxWaitTime ]
        delayedHints = self.__hintRequests
        if not delayedHints:
            return
        maxPriorityHint = max(delayedHints, key=lambda r: r.hint.priority)
        delayedHints.remove(maxPriorityHint)
        component, hint, data, _ = maxPriorityHint
        self.__showHint(component, hint, data)

    def __showHint(self, component, hint, data):
        component.showHint(hint, data)
        self.__currentHint = hint
        self.__hintStartTime = time.time()
        duration = hint.duration
        if duration is not None:
            self.__hideHintCallback()
            self.__hideCallback = BigWorld.callback(duration, partial(self.__hideCurrentHint, component))
        return

    def __hideCurrentHint(self, component):
        self.__hideHintCallback()
        component.hideHint()
        self.__currentHint = None
        self.__showDelayedHint()
        return

    def __hideHintCallback(self):
        if self.__hideCallback is not None:
            BigWorld.cancelCallback(self.__hideCallback)
            self.__hideCallback = None
        return


def createBattleHintsController():
    return BattleHintsController(battle_hints.makeHintsData())
