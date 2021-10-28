# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints_ctrl.py
import time
import logging
from collections import namedtuple
import BigWorld
import SoundGroups
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import battle_hints, g_eventBus, EVENT_BUS_SCOPE, events
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
HintRequest = namedtuple('HintRequest', ('hint', 'data', 'requestTime'))

class BattleHintComponent(object):
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

    def finishHint(self):
        if self.__hideCallback is not None:
            BigWorld.cancelCallback(self.__hideCallback)
            self.__hideCallback = None
        self._finishHint()
        return

    def removeHintFromQueue(self, hint):
        if not self.__hintRequests:
            return
        self.__hintRequests = [ hr for hr in self.__hintRequests if hr.hint != hint ]

    def _showHint(self, hintData, data):
        raise NotImplementedError

    def _hideHint(self):
        raise NotImplementedError

    def _getSoundNotification(self, hint, data):
        return hint.soundNotification

    def _finishHint(self):
        raise NotImplementedError

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
        self._showHint(hint, hint.makeVO(data))
        self.__currentHint = hint
        self.__hintStartTime = time.time()
        self.__fireHintEvent(events.BattleHintEvent.ON_SHOW, hint)
        duration = hint.duration
        if duration is not None:
            self.__hideHintCallback()
            self.__hideCallback = BigWorld.callback(duration, self.__hideCurrentHint)
        return

    def __hideCurrentHint(self):
        self.__hideHintCallback()
        self._hideHint()
        self.__fireHintEvent(events.BattleHintEvent.ON_HIDE, self.__currentHint)
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

    def __fireHintEvent(self, event, hint):
        g_eventBus.handleEvent(events.BattleHintEvent(event, ctx={'hint': hint.name}), scope=EVENT_BUS_SCOPE.BATTLE)


class BattleHintsController(ViewComponentsController):

    def __init__(self, hintsData):
        super(BattleHintsController, self).__init__()
        self.__hintsData = {hint.name:hint for hint in hintsData}

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def clearViewComponents(self):
        for component in self._viewComponents:
            if hasattr(component, 'finishHint'):
                component.finishHint()

        super(BattleHintsController, self).clearViewComponents()

    def showHint(self, hintName, data=None):
        component, hint = self.__getComponentAndHint(hintName)
        if hint and component:
            component.showHint(hint, data)
        else:
            _logger.error('Failed to show hint name=%s', hintName)

    def hideHint(self, hintName):
        component, hint = self.__getComponentAndHint(hintName)
        if hint and component:
            component.hideHint(hint)
        else:
            _logger.error('Failed to hide hint name=%s', hintName)

    def removeHintFromQueue(self, hintName):
        component, hint = self.__getComponentAndHint(hintName)
        if hint and component:
            component.removeHintFromQueue(hint)
        else:
            _logger.error('Failed to remove hint from queue=%s', hintName)

    def __getComponentAndHint(self, hintName):
        component = None
        hint = self.__hintsData.get(hintName)
        if hint:
            alias = hint.componentAlias
            component = findFirst(lambda comp: comp.getAlias() == alias, self._viewComponents)
            if not component:
                _logger.error('Unknown component alias=%s', alias)
        else:
            _logger.error('Unknown hint name=%s', hintName)
        return (component, hint)


def createBattleHintsController():
    return BattleHintsController(battle_hints.makeHintsData())
