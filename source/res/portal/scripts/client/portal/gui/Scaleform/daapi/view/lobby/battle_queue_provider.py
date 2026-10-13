# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/lobby/battle_queue_provider.py
import constants
from gui import makeHtmlString
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.battle_queue import QueueProvider, TYPES_ORDERED
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.formatters import text_styles
from helpers.i18n import makeString
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'

class PortalQueueProvider(QueueProvider):

    def processQueueInfo(self, qInfo):
        info = dict(qInfo)
        if 'classes' in info:
            vClasses = info['classes']
            vClassesLen = len(vClasses)
        else:
            vClasses = []
            vClassesLen = 0
        self._createCommonPlayerString(sum(vClasses))
        if vClassesLen:
            vClassesData = []
            for vClass, message in TYPES_ORDERED:
                idx = constants.VEHICLE_CLASS_INDICES[vClass]
                vClassesData.append({'type': message,
                 'icon': getTypeBigIconPath(vClass),
                 'count': vClasses[idx] if idx < vClassesLen else 0})

            self._proxy.as_setDPS(vClassesData)
        self._proxy.as_showStartS(self._isStartButtonDisplayed(vClasses))

    def additionalInfo(self):
        return text_styles.main(makeString(MENU.PREBATTLE_WAITINGTIMEWARNING))

    @staticmethod
    def _isStartButtonDisplayed(vClasses):
        return False

    def _createCommonPlayerString(self, playerCount):
        self._proxy.flashObject.as_setPlayers(makeHtmlString(_HTMLTEMP_PLAYERSLABEL, 'players', {'count': playerCount}))
