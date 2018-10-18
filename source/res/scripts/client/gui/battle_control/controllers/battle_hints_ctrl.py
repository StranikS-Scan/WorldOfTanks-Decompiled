# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints_ctrl.py
import logging
from gui.battle_control.view_components import IViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
_logger = logging.getLogger(__name__)

class IBattleHintComponent(object):

    def showHint(self, hintID, data):
        handler = self._getHintHandler(hintID)
        if callable(handler):
            handler(data)
        else:
            _logger.error('Failed to get handler for hintID=%s', hintID)

    def closeHint(self):
        raise NotImplementedError

    def _getHintHandler(self, hintType):
        raise NotImplementedError


class BattleHintsController(IViewComponentsController):

    def __init__(self, setup):
        super(BattleHintsController, self).__init__()
        self.__uiComponent = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def stopControl(self):
        pass

    def setViewComponents(self, *components):
        self.__uiComponent = components[0]

    def startControl(self, *args):
        pass

    def clearViewComponents(self):
        if self.__uiComponent:
            self.__uiComponent.closeHint()
            self.__uiComponent = None
        return

    def showHint(self, hintID, data=None):
        if self.__uiComponent:
            self.__uiComponent.showHint(hintID, data)


def createBattleHintsController(setup):
    return BattleHintsController(setup)
