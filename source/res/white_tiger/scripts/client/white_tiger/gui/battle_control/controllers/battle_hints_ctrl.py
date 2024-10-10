# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/battle_hints_ctrl.py
import logging
import time
import BigWorld
import constants
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from gui.shared.battle_hints import BattleHintData
from gui.battle_control.controllers.battle_hints_ctrl import HintRequest
from shared_utils import findFirst
_logger = logging.getLogger(__name__)

class WTBattleHintsController(ViewComponentsController):
    _DEFAULT_HINT_NAME = 'default'
    _OVERTIME_HINT_PREFIX = 'wtOvertime_'

    def __init__(self, hintsData):
        super(WTBattleHintsController, self).__init__()
        self.__hintsData = {hint.name:hint for hint in hintsData}
        self.__currentComponent = None
        self.__delayedHints = []
        self.__currentHintCallback = None
        self.__currentHints = set()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.__cancelCurrentHintCallback()

    def showHint(self, hintName, data=None):
        hint = self.__getHint(hintName)
        if hint:
            if 'param1' in data and hintName.startswith(self._OVERTIME_HINT_PREFIX):
                data['elapsed'] = float(data['param1'])
            if self.__currentComponent:
                self.__resolveHintsConflict(hint, data)
            else:
                self.__currentHints.add(hintName)
                for view in self.__iterComponentsByAlias(hint.componentAlias):
                    view.showHint(hint, data)
                    self.__currentComponent = view
                    if hint.duration is not None:
                        self.__cancelCurrentHintCallback()
                        self.__currentHintCallback = BigWorld.callback(hint.duration, self.__hideHintCallback)

        return

    def hideHint(self, hintName):
        hint = self.__getHint(hintName)
        if hint and hintName in self.__currentHints:
            self.__currentHints.remove(hintName)
            for view in self.__iterComponentsByAlias(hint.componentAlias):
                view.hideHint(hint)
                if view == self.__currentComponent:
                    self.__cancelCurrentHintCallback()
                    self.__currentComponent = None
                self.__showDelayedHint()

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

    def __getHint(self, hintName):
        hint = self.__hintsData.get(hintName)
        if hint is None and constants.IS_DEVELOPMENT:
            hint = self.__hintsData.get(self._DEFAULT_HINT_NAME)
            hint = hint._replace(rawMessage=hintName)
        if not hint:
            _logger.warning('Unknown hint name=%s', hintName)
        return hint

    def __showDelayedHint(self):
        currentTime = time.time()
        self.__delayedHints = [ r for r in self.__delayedHints if currentTime - r.requestTime < r.hint.maxWaitTime ]
        if self.__delayedHints:
            maxPriorityHint = max(self.__delayedHints, key=lambda request: request.hint.priority)
            self.__delayedHints.remove(maxPriorityHint)
            hint, data, _ = maxPriorityHint
            self.showHint(hint.name, data)

    def __iterComponentsByAlias(self, componentAliases):
        for alias in componentAliases:
            component = findFirst(lambda comp, cAlias=alias: comp.getAlias() == cAlias, self._viewComponents)
            if component:
                yield component
            _logger.error('Unknown component alias=%s', alias)
