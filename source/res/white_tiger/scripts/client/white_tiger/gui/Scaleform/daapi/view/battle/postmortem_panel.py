# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/postmortem_panel.py
import logging
from items import vehicles
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel, _ALLOWED_EQUIPMENT_DEATH_CODES
_logger = logging.getLogger(__name__)

class WhiteTigerPostmortemPanel(PostmortemPanel):

    def _onShowVehicleMessageByCode(self, code, postfix, entityID, extra, equipmentID, ignoreMessages):
        if equipmentID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if code not in _ALLOWED_EQUIPMENT_DEATH_CODES and equipment:
                code = '_'.join((code, equipment.messagePostfix))
                self._prepareMessage(code, entityID, self._getDevice(extra))
                return
        super(WhiteTigerPostmortemPanel, self)._onShowVehicleMessageByCode(code, postfix, entityID, extra, equipmentID, ignoreMessages)
