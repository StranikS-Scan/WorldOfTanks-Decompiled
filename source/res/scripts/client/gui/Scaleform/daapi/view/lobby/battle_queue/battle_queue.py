# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue/battle_queue.py
import constants
from CurrentVehicle import g_currentVehicle
from gui.prb_control import prb_getters
from gui.Scaleform.daapi.view.lobby.battle_queue.base_queue import BattleQueueBase
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.Scaleform.locale.MENU import MENU

class BattleQueue(BattleQueueBase):

    def _getVO(self):
        vehicle = g_currentVehicle.item
        guiType = prb_getters.getArenaGUIType(queueType=self._provider.getQueueType())
        if guiType != constants.ARENA_GUI_TYPE.UNKNOWN and guiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
            iconLabel = constants.ARENA_GUI_TYPE_LABEL.LABELS[guiType]
        else:
            iconLabel = 'neutral'
        return {'iconLabel': iconLabel,
         'title': MENU.loading_battletypes(guiType),
         'description': MENU.loading_battletypes_desc(guiType),
         'additional': self._provider.additionalInfo() if self._provider.needAdditionalInfo() else '',
         'tankLabel': text_styles.main(self._provider.getTankInfoLabel()),
         'tankIcon': getTypeBigIconPath(vehicle.type),
         'tankName': vehicle.shortUserName}
