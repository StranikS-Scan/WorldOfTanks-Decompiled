# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/lobby/battle_queue_provider.py
from __future__ import absolute_import
import constants
from gui import makeHtmlString
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.lobby.battle_queue.battle_queue import QueueProvider, TYPES_ORDERED, needShowLongWaitingWarning
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.formatters import text_styles
from helpers.i18n import makeString
_HTMLTEMP_PLAYERSLABEL = 'html_templates:lobby/queue/playersLabel'
_FOUR_ROWS_BATTLE_QUEUE_LAYOUT = 'fourRowsBattleQueue'
_FORT_RUSH_BATTLE_ICON = backport.image(R.images.gui.maps.icons.battleTypes.c_136x136.fort_rush_battle())
_FORT_RUSH_BATTLE_QUEUE_TITLE = backport.text(R.strings.fort_rush.battleQueue.title())
_FORT_RUSH_EXCLUDED_BATTLE_QUEUE_CLASS = tuple(['SPG'])

class FortRushQueueProvider(QueueProvider):

    def __init__(self, proxy, qType=constants.QUEUE_TYPE.UNKNOWN):
        super(FortRushQueueProvider, self).__init__(proxy, qType)
        self._needAdditionalInfo = None
        return

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
                if vClass not in _FORT_RUSH_EXCLUDED_BATTLE_QUEUE_CLASS:
                    idx = constants.VEHICLE_CLASS_INDICES[vClass]
                    vClassesData.append({'type': message,
                     'icon': getTypeBigIconPath(vClass),
                     'count': vClasses[idx] if idx < vClassesLen else 0})

            self._proxy.as_setDPS(vClassesData)
        self._proxy.as_showStartS(self._isStartButtonDisplayed(vClasses))

    def needAdditionalInfo(self):
        if self._needAdditionalInfo is None:
            self._needAdditionalInfo = needShowLongWaitingWarning()
        return self._needAdditionalInfo

    def getLayoutStr(self):
        return _FOUR_ROWS_BATTLE_QUEUE_LAYOUT

    def getIconPath(self, iconLabel):
        return _FORT_RUSH_BATTLE_ICON

    def getTitle(self, guiType):
        return _FORT_RUSH_BATTLE_QUEUE_TITLE

    def additionalInfo(self):
        return text_styles.main(makeString(MENU.PREBATTLE_WAITINGTIMEWARNING))

    @staticmethod
    def _isStartButtonDisplayed(vClasses):
        return False

    def _createCommonPlayerString(self, playerCount):
        self._proxy.flashObject.as_setPlayers(makeHtmlString(_HTMLTEMP_PLAYERSLABEL, 'players', {'count': playerCount}))
