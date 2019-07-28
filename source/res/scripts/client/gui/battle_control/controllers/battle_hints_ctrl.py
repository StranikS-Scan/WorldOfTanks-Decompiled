# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints_ctrl.py
import heapq
import logging
from functools import partial
import BigWorld
import SoundGroups
from gui.battle_control import avatar_getter
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import battle_hints
_logger = logging.getLogger(__name__)

class BattleHintComponent(object):

    def __init__(self):
        super(BattleHintComponent, self).__init__()
        self.__currentHint = None
        self.__delayedHints = []
        self.__hideCallback = None
        return

    def showHint(self, hint, data):
        currentHint = self.__currentHint
        if currentHint:
            if currentHint.priority <= hint.priority:
                heapq.heappush(self.__delayedHints, (hint.priority, (hint, data)))
            else:
                self.__hideCurrentHint()
                self.__showHint(hint, data)
        else:
            self.__showHint(hint, data)

    def hideHint(self, hint):
        if self.__currentHint == hint:
            self.__hideCurrentHint()
            self.__showDelayedHint()
        else:
            _logger.warning('Failed to hide hint name=%s', hint.name)

    def finishHint(self):
        self._finishHint()

    def _showHint(self, hintData, data):
        raise NotImplementedError

    def _hideHint(self):
        raise NotImplementedError

    def _finishHint(self):
        raise NotImplementedError

    def __showHint(self, hint, data):
        if hint.soundFx is not None:
            SoundGroups.g_instance.playSound2D(hint.soundFx)
        if hint.soundNotification is not None:
            avatar_getter.getSoundNotifications().play(hint.soundNotification)
        self._showHint(hint, data)
        self.__currentHint = hint
        duration = hint.duration
        if duration is not None:
            self.__hideCallback = BigWorld.callback(duration, partial(self.__hideHintCallback, hint))
        return

    def __hideCurrentHint(self):
        hideCallback = self.__hideCallback
        if hideCallback:
            BigWorld.cancelCallback(hideCallback)
            self.__hideCallback = None
        self._hideHint()
        self.__currentHint = None
        return

    def __hideHintCallback(self, hint):
        self.__hideCallback = None
        self.hideHint(hint)
        return

    def __showDelayedHint(self):
        delayedHints = self.__delayedHints
        if delayedHints:
            _, (delayedHint, data) = heapq.heappop(delayedHints)
            self.__showHint(delayedHint, data)


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

    def __getComponentAndHint(self, hintName):
        component = None
        hint = self.__hintsData.get(hintName)
        if hint:
            alias = hint.componentAlias
            for comp in self._viewComponents:
                if comp.getAlias() == alias:
                    component = comp
                    break

            if not component:
                _logger.error('Unknown component alias=%s', alias)
        else:
            _logger.error('Unknown hint name=%s', hintName)
        return (component, hint)


def createBattleHintsController():
    return BattleHintsController(battle_hints.makeHintsData())
