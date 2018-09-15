# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/alert_message_block.py
from gui.Scaleform.daapi.view.meta.AlertMessageBlockMeta import AlertMessageBlockMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
from helpers import time_utils

class AlertMessageBlock(AlertMessageBlockMeta):

    def __init__(self):
        super(AlertMessageBlock, self).__init__()

    def updateTimeLeft(self, timeLeft):
        self.__update(timeLeft)

    def _populate(self):
        self.__update()

    def __update(self, timeLeft=0):
        timeLeftStr = time_utils.getTillTimeString(timeLeft, RANKED_BATTLES.STATUS_TIMELEFT)
        statusText = text_styles.vehicleStatusCriticalText(_ms(RANKED_BATTLES.PRIMETIMEALERTMESSAGEBLOCK_MESSAGE, time=timeLeftStr))
        self.as_setDataS({'alertIcon': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
         'buttonIcon': RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR,
         'buttonLabel': '',
         'buttonVisible': True,
         'buttonTooltip': makeTooltip(RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_BODY),
         'statusText': statusText,
         'popoverAlias': RANKEDBATTLES_ALIASES.RANKED_BATTLES_CALENDAR_POPOVER,
         'bgVisible': True,
         'shadowFilterVisible': True})
