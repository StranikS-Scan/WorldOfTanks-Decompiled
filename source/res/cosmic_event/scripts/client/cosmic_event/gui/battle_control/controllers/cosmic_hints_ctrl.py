# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_control/controllers/cosmic_hints_ctrl.py
import logging
from cosmic_event.settings import HINTS
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
_logger = logging.getLogger(__name__)

class CosmicBattleHintsController(ViewComponentsController):

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def showHint(self, hintName, data=None):
        hint = self.__getHint(hintName)
        if hint:
            _logger.debug('Request battle hint hintName=%s', hintName)
            for component in self._viewComponents:
                component.showHint(hint, data)

        else:
            _logger.error('Failed to show hint name=%s', hintName)

    def hideHint(self, hintName):
        hint = self.__getHint(hintName)
        if hint:
            for component in self._viewComponents:
                component.hideHint(hint)

        else:
            _logger.error('Failed to hide hint name=%s', hintName)

    def setScanningVehicles(self, scanningVehicles):
        for component in self._viewComponents:
            component.setScanningVehicles(scanningVehicles)

    def __getHint(self, hintName):
        hint = HINTS.get(hintName)
        if not hint:
            _logger.error('Unknown hint name=%s', hintName)
        return hint
