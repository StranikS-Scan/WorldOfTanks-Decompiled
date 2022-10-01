# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/postmortem_panel.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel, _ALLOWED_EQUIPMENT_DEATH_CODES
from gui.Scaleform.daapi.view.meta.BattleRoyalePostmortemPanelMeta import BattleRoyalePostmortemPanelMeta
from items import vehicles

class BattleRoyalePostmortemPanel(PostmortemPanel, BattleRoyalePostmortemPanelMeta):

    def _onShowVehicleMessageByCode(self, code, postfix, entityID, extra, equipmentID, ignoreMessages):
        if equipmentID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if code not in _ALLOWED_EQUIPMENT_DEATH_CODES and equipment:
                code = '_'.join((code, equipment.name.upper()))
                self._prepareMessage(code, entityID, self._getDevice(extra))
                return
        super(BattleRoyalePostmortemPanel, self)._onShowVehicleMessageByCode(code, postfix, entityID, extra, equipmentID, ignoreMessages)
