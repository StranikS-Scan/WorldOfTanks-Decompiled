# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/postmortem_panel.py
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import _ALLOWED_EQUIPMENT_DEATH_CODES
from gui.Scaleform.daapi.view.meta.BattleRoyalePostmortemPanelMeta import BattleRoyalePostmortemPanelMeta
from gui.shared.gui_items import Vehicle
from items import vehicles

class BattleRoyalePostmortemPanel(BattleRoyalePostmortemPanelMeta):

    def __init__(self):
        super(BattleRoyalePostmortemPanel, self).__init__()
        bonusType = BigWorld.player().arenaBonusType
        self.__isBattleRoyaleTournament = bonusType in (ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SQUAD)
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        self.__isObserver = 'observer' in vehicle.typeDescriptor.type.tags if vehicle else False

    def _onShowVehicleMessageByCode(self, code, postfix, entityID, extra, equipmentID, ignoreMessages):
        if equipmentID:
            equipment = vehicles.g_cache.equipments().get(equipmentID)
            if code not in _ALLOWED_EQUIPMENT_DEATH_CODES and equipment:
                code = '_'.join((code, equipment.name.upper()))
                self._prepareMessage(code, entityID, self._getDevice(extra))
                return
        super(BattleRoyalePostmortemPanel, self)._onShowVehicleMessageByCode(code, postfix, entityID, extra, equipmentID, ignoreMessages)

    def _populate(self):
        super(BattleRoyalePostmortemPanel, self)._populate()
        if self.__isBattleRoyaleTournament and self.__isObserver:
            self.as_setPostmortemPanelVisibleS(False)

    def _showOwnDeathInfo(self):
        if not self._deathAlreadySet:
            deathInfo = self.getDeathInfo()
            if deathInfo is not None and self.__isBattleRoyaleBotVehicle(deathInfo['killerVehicle']):
                killerInfo = self.sessionProvider.getCtx().getArenaDP().getVehicleInfo(deathInfo['killerVehicle'])
                reason = self._makeReasonInfo(deathInfo)
                vehicleType = Vehicle.getTypeVPanelIconPath(killerInfo.vehicleType.classTag)
                vehicleName = killerInfo.vehicleType.shortNameWithPrefix
                self.as_setDeadReasonInfoS(reason, True, '', '', vehicleType, vehicleName, None)
                self._deathAlreadySet = True
                return
        super(BattleRoyalePostmortemPanel, self)._showOwnDeathInfo()
        return

    def _prepareMessage(self, code, killerVehID, device=None):
        if self.__isBattleRoyaleBotVehicle(killerVehID):
            msgText, colors = self._messages['DEATH_FROM_BR_BOT']
            self._deathInfo = {'text': msgText,
             'colors': colors,
             'killerVehicle': killerVehID,
             'device': device}
            self._deathInfoReceived()
        else:
            super(BattleRoyalePostmortemPanel, self)._prepareMessage(code, killerVehID, device)

    def _updateVehicleInfo(self):
        if not (self._isInPostmortem or self.__isObserver):
            return
        if self._isPlayerVehicle or self.__isObserver:
            if self.__isBattleRoyaleTournament and not self.__isObserver:
                return
            self._showOwnDeathInfo()
        else:
            self._showPlayerInfo()

    def __isBattleRoyaleBotVehicle(self, vehicleID):
        if vehicleID is None:
            return False
        else:
            vehicleInfoVO = self.sessionProvider.getCtx().getArenaDP().getVehicleInfo(vehicleID)
            return vehicleInfoVO.team == 21
