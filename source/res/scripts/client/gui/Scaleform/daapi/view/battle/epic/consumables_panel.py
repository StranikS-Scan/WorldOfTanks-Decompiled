# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/consumables_panel.py
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.genConsts.CONSUMABLES_PANEL_SETTINGS import CONSUMABLES_PANEL_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers.epic_game import searchRankForSlot
from items.vehicles import getVehicleClassFromVehicleType

class EpicBattleConsumablesPanel(ConsumablesPanel):
    _EMPTY_LOCKED_SLOT = -1
    _GLOW_DELAY = 0.5
    _EPIC_EQUIPMENT_ICON_PATH = '../maps/icons/epicBattles/skills/48x48/%s.png'

    def __init__(self):
        super(EpicBattleConsumablesPanel, self).__init__()
        self.__battleReserveSlots = dict()
        self.__glowUpdateInfo = dict()

    def _getPanelSettings(self):
        return CONSUMABLES_PANEL_SETTINGS.EPIC_BATTLE_SETTINGS_ID

    def _reset(self):
        super(EpicBattleConsumablesPanel, self)._reset()
        self.__battleReserveSlots.clear()

    def _addEquipmentSlot(self, idx, intCD, item):
        super(EpicBattleConsumablesPanel, self)._addEquipmentSlot(idx, intCD, item)
        if idx < self._ORDERS_START_IDX:
            return
        elif item is None:
            return
        else:
            if idx not in self.__battleReserveSlots:
                self.__battleReserveSlots[idx] = (intCD, item.getQuantity())
                self.__addEquipmentLevelToSlot(idx, item)
                self.__addLockedInformationToEpicEquipment(idx)
            return

    def _getEquipmentIcon(self, idx, icon):
        return self._EPIC_EQUIPMENT_ICON_PATH % icon if idx in self.__battleReserveSlots else super(EpicBattleConsumablesPanel, self)._getEquipmentIcon(idx, icon)

    def _resetEquipmentSlot(self, idx, intCD, item):
        super(EpicBattleConsumablesPanel, self)._resetEquipmentSlot(idx, intCD, item)
        if idx not in self.__battleReserveSlots:
            return
        self.__battleReserveSlots[idx] = (intCD, item.getQuantity())
        self.__addEquipmentLevelToSlot(idx, item)
        if item.getQuantity() > 0:
            self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_UPGRADE
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)

    def _updateEquipmentSlot(self, idx, item):
        super(EpicBattleConsumablesPanel, self)._updateEquipmentSlot(idx, item)
        if idx not in self.__battleReserveSlots:
            return
        _, prevQuantity = self.__battleReserveSlots[idx]
        if prevQuantity < item.getQuantity():
            self.as_updateLockedInformationS(idx, self._EMPTY_LOCKED_SLOT, '')
            self.__battleReserveSlots[idx] = (self._cds[idx], item.getQuantity())
            self.__glowUpdateInfo[idx] = CONSUMABLES_PANEL_SETTINGS.GLOW_ID_GREEN_UNLOCK
            self.delayCallback(self._GLOW_DELAY, self.__updateEquipmentGlowCB)

    def __updateEquipmentGlowCB(self):
        for idx in self.__glowUpdateInfo:
            self.as_setGlowS(idx, self.__glowUpdateInfo[idx])

        self.__glowUpdateInfo.clear()

    def __addLockedInformationToEpicEquipment(self, idx):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComp is None:
            return
        else:
            arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
            vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
            vehClass = getVehicleClassFromVehicleType(vehicle.typeDescriptor.type)
            if arena is None:
                return
            slotEventsConfig = arena.settings.get('epic_config', {}).get('epicMetaGame', {}).get('inBattleReservesByRank').get('slotActions', {}).get(vehClass, {})
            if not slotEventsConfig:
                return
            unlockedSlotIdx = idx - self._ORDERS_START_IDX
            rank = searchRankForSlot(unlockedSlotIdx, slotEventsConfig)
            if rank is None:
                return
            currentRank = playerDataComp.playerRank if playerDataComp.playerRank is not None else 0
            if rank <= currentRank - 1:
                return
            rank += 1
            tooltipId = TOOLTIPS_CONSTANTS.EPIC_RANK_UNLOCK_INFO if rank > 1 else ''
            self.as_updateLockedInformationS(idx, rank, tooltipId)
            return

    def __addEquipmentLevelToSlot(self, idx, item):
        itemName = item.getDescriptor().name
        if 'level' not in itemName:
            return
        levelStr = itemName.partition('level')[-1]
        if not levelStr.isdigit():
            return
        self.as_updateLevelInformationS(idx, int(levelStr))
